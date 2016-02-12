from aiweb_tools.games import engine
from aiweb_tools.games.tron_game import tron
from aiweb_tools.games import Game
from aiweb_tools import games

import os.path

from aiweb_tools import config

test_map_path = config.map_path + "test_map.map"

class Tron(games.Game):

	def __init__(self, opts, players, player_names, map_path="", teams=[]):
		#self.opts = opts
		self.gamename = "Tron"
		if map_path == "":
			self.map_path = test_map_path
			turns = 10
		else:
			self.map_path = map_path
			turns = 1000
		self.opts = {
			## ants/engine opts:  (see http://aichallenge.org/game_settings.php)
			'turns':turns,	
			'loadtime': 5000,
			'turntime': 500,
			'cutoff_percent': 0.85,
			'cutoff_turn': 150,
			'kill_points': 2,
			'secure_jail' : True,
			'capture_errors' : True,
		}
		self.players = players
		self.player_names = player_names
		#self.teams = teams

	def run_game(self):
		#map_path = os.path.join(maps_path, temp_map)
		print("map path: " + str(self.map_path))
		with open(self.map_path) as fo:
			map_text = "".join(fo.readlines())
		self.opts['map'] = map_text
		game = tron.Tron(self.opts)
		game_result = engine.run_game(game, self.players, self.opts)
		game_result['playernames'] = self.player_names
		print(game_result)
		return game_result

 
Game = Tron
