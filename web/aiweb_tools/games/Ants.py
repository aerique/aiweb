from aiweb_tools.games import engine
from aiweb_tools.games.ants_game import ants
from aiweb_tools.games import Game
from aiweb_tools import games

import os.path

from aiweb_tools import config

maps_path =  "/home/" + config.username + "/aiweb/ants/maps/"
temp_map = "temp_map.map"

class Ants(games.Game):
	gamename = "Ants"
	opts = {
		## ants/engine opts:  (see http://aichallenge.org/game_settings.php)
		'turns':1000,	# 1500 on aichallenge
		'loadtime': 5000,
		'turntime': 5000,
		'viewradius2': 77,
		'attackradius2': 5,
		'spawnradius2': 1,
		'attack': 'focus',
		'food': 'symmetric',
		'food_rate': (5,11), # total food
		'food_turn': (19,37), # per turn
		'food_start': (75,175), # per land area
		'food_visible': (3,5), # in starting loc
		'cutoff_percent': 0.85,
		'cutoff_turn': 150,
		'kill_points': 2,
	}

	def __init__(self, opts, players, teams=[]):
		#self.opts = opts
		self.players = players
		#self.teams = teams

	def run_game(self):
		map_path = os.path.join(maps_path, temp_map)
		with open(map_path) as fo:
			map_text = "".join(fo.readlines())
		self.opts['map'] = map_text
		game = ants.Ants(self.opts)
		engine.run_game(game, self.players, self.opts)

 
Game = Ants
