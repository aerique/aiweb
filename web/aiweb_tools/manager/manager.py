import logging
import subprocess
import datetime
import glob
import cloudpickle 
import json

import sys
from django.core.management.base import BaseCommand

import aiweb.models
import aiweb_tools.comms

from .. import config

def send_submission (filepath, destname):

	# FIXME No checking for return codes
	# FIXME not using port


	subprocess.call(["sync"])
	subprocess.call(["scp", filepath, config.datastore_username + "@" + 
					config.datastore_ip + "://" +
					config.datastore_submission_path + destname]);
	subprocess.call(["rm", filepath]);

def add_task(ip_addr, prefix, file_content):
	srcname = prefix + config.delimiter + (datetime.datetime.now().isoformat()).replace(":", "-")
	f = open(srcname, 'w')
	f.write(file_content)
	f.close()
	subprocess.call(["scp", srcname, config.task_username + "@" + 
					ip_addr + "://" +
					config.task_path ]);
	subprocess.call(["rm", srcname])

def detect_game(filepath):
	filename = filepath.split('/')[-1]
	result = None
	for game in config.games_active:
		if filename.lower().startswith(game.lower()):
			result = game
	return result

def handle_submission(filepath, username):

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


		send_submission (filepath, destname)
		add_submission_report(username, gamename, timestamp, destname, "Uncompiled", "Unknown", "")

	# FIXME better protection against filename collisions desirable
	add_task (config.task_ip, "compile", "compile " + destname)

def send_task_to_worker(task, worker_file):
	print("send_task_to_worker")
	with open(worker_file) as worker_fo:
		worker_ip = worker_fo.readline().strip()
		worker_id = worker_fo.readline().strip()
	print(worker_ip)
	with open (task, "a") as taskfile:
		taskfile.write(" " + worker_id)
	print("id = " + worker_id)
	aiweb_tools.comms.send_task_worker_ip(task, worker_ip)
	subprocess.call(["rm", task])

def find_game(worker_file):
	aiweb_tools.comms.send_file_matchmaker_ready(worker_file, config.matchmaker_path)

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
		print ("considering task file: " + file)
		ending = ".ready"
		if (file.endswith(ending)):
			real = file[:-len(ending)]
			print(real)
			if find_task(real):
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
	print("processing reports")
	for file in glob.glob(config.webserver_results_path + "*-report.txt.ready"):
		process_report(file, add_submission_report)


def add_submission_report(username, game, timestamp, prefix, status, language, content):
	subm_list = aiweb.models.Submission.objects.filter(username=username, game_id = game, timestamp = timestamp, submission_id = prefix)
	if len(subm_list) < 1:
		subm = aiweb.models.Submission.objects.create(
			user = aiweb.models.User.objects.get(username=username),
			username = username,
			game_id = game,
			timestamp = timestamp,
			submission_id = prefix,
			status = status,
			language = language,
			report = content)
	else:
		subm = subm_list[0]
		subm.status = status
		subm.language = language
		subm.report = content

	subm.save()

def process_match_results():
	print("processing match results")
	for file in glob.glob(config.webserver_results_path + "*-match-result.txt.ready"):
		process_match_result(file)
	
def process_match_result(path):
	real = path[:-len('.ready')]
	print("processing match result: " + real)
	with open(real, 'rb') as fo:
		result_dict = cloudpickle.load(fo)
		replay_id = aiweb_tools.comms.get_replay_id()
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
		result = aiweb.models.Result.objects.create(
			player_names = " ".join(result_dict['playernames']),
			scores = scores,
			statuses = status,
			ranks = rank,
			game_message = "",
			replay = replay_path.split("/")[-1])
		result.save()

		if 'replaydata' in result_dict:
			replay = result_dict['replaydata']
			replay['gamename'] = result_dict['challenge']
			with open(replay_path, 'w') as fo:
				json.dump(replay, fo)

	subprocess.call(["rm", real])
	subprocess.call(["rm", path])
	

