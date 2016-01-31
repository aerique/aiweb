import aiweb_tools.comms
import datetime
import time

from aiweb_tools import config
import glob
import subprocess
import os.path
import aiweb.models
import aiweb_tools.games
import random

class Matchmaker:
	def await_request(self):
		stopfile = (config.matchmaker_path + "stop_matchmaker") 
		while not os.path.isfile(stopfile):
			ready = ".ready"
			for file in glob.glob(config.matchmaker_path + "*" + ready):
				print(file)
				real = (file[:-len(ready)])
				self.process_request(real)
				subprocess.call(["rm", real])
				subprocess.call(["rm", file])
			time.sleep(5)
			print("checking for requests")

		subprocess.call(["rm", stopfile])

	def process_request(self, filepath):
		filename = aiweb_tools.comms.filename(filepath)
		if filename.startswith('compiled'):
			self.add_compile_data(filepath)
		else:
			match = self.make_match()
			self.send_match_to_worker(match, filepath)

	def add_compile_data(self, filepath):
		with open(filepath) as fo:
			username = fo.readline().strip()
			game_id = fo.readline().strip()
			submission_id = fo.readline().strip()
			# add to matchmaker db
			bot_list = aiweb.models.Bot.objects.using('matchmaker').filter(username=username, game_id=game_id)
			if len(bot_list) < 1:
				self.add_new_bot(username, game_id, submission_id)
			else:
				bot = bot_list[0]
				bot.submission_id = submission_id
				bot.compile_time = datetime.datetime.now()
				bot.games_played = 0
				bot.save()
				
	def add_new_bot(self, username, game_id, submission_id):
		bot = aiweb.models.Bot()
		bot.username = username
		bot.game_id = game_id
		bot.submission_id = submission_id
		bot.compile_time = datetime.datetime.now()
		bot.games_played = 0
		bot.save(using='matchmaker')

	def  send_match_to_worker(self, match, workerfile):
		#FIXME currently this sends workerfile back to task pool
		aiweb_tools.comms.send_file_taskserver_ready(workerfile, config.task_worker_path)

	def make_match(self):
		games = config.games_running
		gamename = random.choice(games)
		print("chosen " + gamename)
		#bots = aiweb.models.Bot.objects.using('matchmaker').filter(game_id = gamename).order_by('selection_weight')
		bots = aiweb.models.Bot.objects.using('matchmaker').all()
		num_bots = bots.count()

		game = aiweb_tools.games.get_game(gamename)

		print ("Need: " + str(game.min_players))
		print ("Have: " + str(num_bots))

		if num_bots < game.min_players:
			print ("Not enough bots to play " + gamename)
			print ("Need: " + str(game.min_players))
			print ("Have: " + str(num_bots))
			return False
		else:
			selected = self.select_random_players(game.min_players, num_bots)
			print(selected)
			for i in selected:
				print(bots[i].username)
				print(bots[i].game_id)
				print(bots[i].submission_id)
			return True

	def select_random_players(self, num_players, num_bots):
		result = []
		while len(result) < num_players:
			selected = random.randint(0, num_bots - 1)
			if selected in result:
				pass
			else:
				result.append(selected)
		return result
