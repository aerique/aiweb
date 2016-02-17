import logging
import subprocess
import datetime
import glob
import cloudpickle 
import json
import skills
import skills.trueskill

import sys
from django.core.management.base import BaseCommand

import aiweb.models
from aiweb_tools import comms

from . import config

def detect_game(filepath):
	filename = filepath.split('/')[-1]
	result = None
	for game in config.games_active:
		if filename.lower().startswith(game.lower()):
			result = game
	return result

def handle_submission(filepath, username):
	""" First point of entry from website after submission """

	print("Processing submission at " + filepath);

	gamename = detect_game(filepath)
	timestamp = (datetime.datetime.now().isoformat()).replace(":", "-")
	destname = username + config.delimiter + str(gamename) + config.delimiter + timestamp
	if gamename == None:
		message = "Please submit a zipfile with a filename beginning with the name of one of the active games.\n For example, 'Ants-sub123.zip' is valid, as is 'Tron_abcde.zip'\n Currently active games are:"
		for game in config.games_active:
			message += "\n" + game
		add_submission_report(username, "Undetected", timestamp, destname, "Game not detected", "Unknown", message)
	else:


		comms.send_submission (filepath, destname)
		add_submission_report(username, gamename, timestamp, destname, "Uncompiled", "Unknown", "")

	# FIXME better protection against filename collisions desirable
	comms.add_task (config.task_ip, "compile", "compile " + destname)

def send_task_to_worker(task, worker_file):
	print("send_task_to_worker")
	with open(worker_file) as worker_fo:
		worker_ip = worker_fo.readline().strip()
		worker_id = worker_fo.readline().strip()
	print(worker_ip)
	with open (task, "a") as taskfile:
		taskfile.write(" " + worker_id)
	print("id = " + worker_id)
	comms.send_task_worker_ip(task, worker_ip)
	subprocess.call(["rm", task])

def find_game(worker_file):
	""" Nothing to do, ask for a match. This function should be renamed """
	comms.send_file_matchmaker_ready(worker_file, config.matchmaker_path)

def find_task(worker_file):
	tasks = glob.glob(config.task_path + "*")
	finished = False
	for task in tasks:
		if not finished:
			taskname = task.split("/")[-1]
			if not (taskname.startswith("worker-ready")):
				send_task_to_worker (task, worker_file)
				finished = True
	if not finished:
		find_game(worker_file)
	#return True # return finished
	return True

def assign_tasks():
	#print('Assigning tasks')
#	tasks = glob.glob(task_path + "*")
#	for task in tasks:
#		print("Task: " + task.split("/")[-1])
	for file in glob.glob(config.task_worker_path + "worker-ready*"):
#		print ("considering task file: " + file)
		ending = ".ready"
		if (file.endswith(ending)):
			real = file[:-len(ending)]
			if find_task(real):
				print(real)
				subprocess.call(["rm", file])
				subprocess.call(["rm", real])
	#print('tasks assigned')

def process_report(path, add_submission_report):
	real = path[:-len('.ready')]
	filename = real.split('/')[-1]
	fsplit = filename.split('.')
	prefix = fsplit[0] + "." + fsplit[1].split('-')[0]
	parts = prefix.split(config.delimiter)
	username = parts[0]
	game = parts[1]
	timestamp = parts[2]
	with open(real) as fo:
		status = fo.readline().strip()
		language = fo.readline().strip()
		content = fo.readlines()
		print(username)
		print(game)
		print(timestamp)
		print(prefix)
		print(status)
		print(content)
		add_submission_report(username, game, timestamp, prefix, status, language, "".join(content))
	subprocess.call(["rm", real])
	subprocess.call(["rm", path])


def process_reports(add_submission_report):
#	print("processing reports")
	for file in glob.glob(config.webserver_results_path + "*-report.txt.ready"):
		process_report(file, add_submission_report)


def add_submission_report(username, game, timestamp, prefix, status, language, content):
	subm_list = aiweb.models.Submission.objects.filter(username=username, game_id = game, timestamp = timestamp, submission_id = prefix)
	if len(subm_list) < 1:
		active = False
		if (status == "Ready"):
			active = True
		subm = aiweb.models.Submission.objects.create(
			user = aiweb.models.User.objects.get(username=username),
			username = username,
			game_id = game,
			timestamp = timestamp,
			submission_id = prefix,
			status = status,
			language = language,
			report = content,
			active = active)
	else:
		subm = subm_list[0]
		subm.status = status
		subm.language = language
		subm.report = content

	subm.save()

def process_match_results():
#	print("processing match results")
	for file in glob.glob(config.webserver_results_path + "*-match-result.txt.ready"):
		process_match_result(file)
	
def process_match_result(path):
	""" Read match result from path and save new result object to db """
	real = path[:-len('.ready')]
	print("processing match result: " + real)
	with open(real, 'rb') as fo:
		result_dict = cloudpickle.load(fo)
		replay_id = comms.get_replay_id()
		replay_path = config.webserver_results_path + str(replay_id) + ".replay"
		if 'scores' in result_dict:
			scores = " ".join([str(x) for x in result_dict['score']])
		else:
			scores = ""
		if 'status' in result_dict:
			status= " ".join([str(x) for x in result_dict['status']])
		else:
			status = ""
		if 'rank' in result_dict:
			rank= " ".join([str(x) for x in result_dict['rank']])
		else:
			rank = ""
		errors = []
		if 'errors' in result_dict:
			for error in result_dict['errors']:
				err_obj = aiweb.models.BotError.objects.create(text = error) 
				errors.append(err_obj)
		if 'challenge' in result_dict:			
			result = aiweb.models.Result.objects.create(
				gamename = result_dict['challenge'],
				player_names = " ".join(result_dict['playernames']),
				scores = scores,
				statuses = status,
				ranks = rank,
				game_message = "",
				replay = replay_path.split("/")[-1])
			if 'bot_ids' in result_dict:
				submissions = []
				for bot_id in result_dict['bot_ids']:
					try:
						submission = aiweb.models.Submission.objects.get(submission_id = bot_id)
						result.submissions.add(submission)
						submissions.append(submission)
					except KeyError:
						# FIXME logging
						pass
				if len(submissions) == len(result_dict['rank']):
					update_ranks(submissions, result_dict['rank'])
				else:
					# FIXME logging
					print("num submissions and num ranks differ!")
			for error in errors:
				error.save()
				print(error.text)
				result.bot_errors.add(error)
			result.save()
		else:
			# FIXME logging
			print("Error: 'challenge' not found in result_dict:\n" + str(result_dict))

		if 'replaydata' in result_dict:
			replay = result_dict['replaydata']
			replay['gamename'] = result_dict['challenge']
			with open(replay_path, 'w') as fo:
				json.dump(replay, fo)

	subprocess.call(["rm", real])
	subprocess.call(["rm", path])
	
def update_ranks(submissions, ranks):
	print("update_ranks called")
	print([submission.submission_id for submission in submissions])
	print(ranks)
	#players = [skills.Player(submission.submission_id) for submission in submissions]
#	teams = [skills.Team({skills.Player(submission.submission_id): (submission.mu, submission.sigma)}) for submission in submissions]
	teams = [skills.Team({submission.submission_id: skills.GaussianRating(submission.mu, submission.sigma)}) for submission in submissions]
	match = skills.Match(teams, ranks)
	calc = skills.trueskill.FactorGraphTrueSkillCalculator()
	game_info = skills.trueskill.TrueSkillGameInfo()
	updated = calc.new_ratings(match, game_info)
	print("Updated:")
	for team in updated:
		for player in team.keys():
			submission = next(i for i in submissions if i.submission_id == player.player_id)
			submission.mu = team[player].mean
			submission.sigma = team[player].stdev
			submission.skill = submission.mu - 3 * submission.sigma
			submission.save()
			print(str(player) + "\n")
			print(str(team[player]) + "\n\n")


