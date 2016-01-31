import aiweb_tools.comms
import datetime
import time

from aiweb_tools import config
import glob
import subprocess
import os.path
import aiweb.models

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
			self.make_match_for_worker(filepath)

	def add_compile_data(self, filepath):
		with open(filepath) as fo:
			username = fo.readline()
			game_id = fo.readline()
			submission_id = fo.readline()
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

	def  make_match_for_worker(self, filepath):
		pass
