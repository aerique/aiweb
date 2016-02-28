#   Copyright 2016 The aichallenge Community
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from aiweb_tools import comms
import datetime
import time

from aiweb_tools import config
import glob
import subprocess
import os.path
import aiweb.models
import aiweb_tools.games
import aiweb_tools.match
import aiweb_tools.worker
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
				comms.delete_file(real)
				comms.delete_file(file)
			time.sleep(config.sleeptime)
			#print("checking for requests")

		comms.delete_file(stopfile)

	def process_request(self, filepath):
		filename = comms.filename(filepath)
		if filename.startswith('compiled'):
			self.add_compile_data(filepath)
		else:
			try:
				match = self.make_match()
				self.send_match_to_worker(match, filepath)
			except AssertionError as e:
				comms.send_file_taskserver_ready(filepath, config.task_worker_path)

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
		worker_data = aiweb_tools.worker.Worker_data()
		worker_data.read(workerfile)
		filepath = config.matchmaker_path + "match" + config.delimiter + worker_data.uuid + match.short_string()
		match.set_for_worker(worker_data.uuid)
		match.write_file(filepath)

		comms.send_task_worker_ip(filepath, worker_data.ip_addr)
		comms.delete_file(filepath)

		#aiweb_tools.comms.send_file_taskserver_ready(workerfile, config.task_worker_path)

	def make_match(self):
		""" Select game, players and map and return Match object """
		games = config.games_active
		print(games)
		gamename = random.choice(games)
		print("chosen " + gamename)
		bots = aiweb.models.Bot.objects.using('matchmaker').filter(game_id = gamename).order_by('selection_weight')
		#bots = aiweb.models.Bot.objects.using('matchmaker').all()
		total_num_bots = bots.count()

		game = aiweb_tools.games.get_game(gamename)

		print ("Need: " + str(game.min_players))
		print ("Have: " + str(total_num_bots))

		if total_num_bots < game.min_players:
			print ("Not enough bots to play " + gamename)
			print ("Need: " + str(game.min_players))
			print ("Have: " + str(total_num_bots))
			raise AssertionError("Not enough bots to play " + gamename)
		else:
			# Later change this so the game chooses, in case it wants teams
			bots_to_select = random.randint(game.min_players, min(game.max_players, total_num_bots))
			selected = self.select_random_players(bots_to_select, total_num_bots)
			print(selected)
			print(str(len(selected)))
			match = aiweb_tools.match.Match()
			match.gamename = gamename
			match.map_file = self.select_map(gamename, bots_to_select)
			for i in selected:
				match.add_bot(bots[i].submission_id)
				print(bots[i].username)
				print(bots[i].game_id)
				print(bots[i].submission_id)
			return match

	def select_random_players(self, num_players, num_options):
		result = []
		while len(result) < num_players:
			selected = random.randint(0, num_options - 1)
			if selected in result:
				pass
			else:
				result.append(selected)
		return result

	def select_map(self, gamename, num_bots):
		""" Select a map for num_bots playing gamename """ 
		# Later change this so the game chooses the map
		map_path = config.map_path + gamename + "/"
		print(map_path)
		maps = glob.glob(map_path + "*_p%02d_*.map"%(num_bots,))
		print(str(maps))
		if len(maps) < 1:
			maps = glob.glob(map_path + "*.map".format(num_bots))
			if len(maps) < 1:
				raise FileNotFoundError("No maps for " + str(num_bots) + " bots playing " + gamename)
			else:
				return random.choice(maps)
		else:
			return random.choice(maps)
