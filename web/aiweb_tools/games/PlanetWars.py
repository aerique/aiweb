from aiweb_tools.games import engine
from aiweb_tools.games.planetwars_game import planetwars
from aiweb_tools.games import Game
from aiweb_tools import games

import os.path

from aiweb_tools import config

test_map_path = config.map_path + "PlanetWars/test_map.map"

class PlanetWars(games.Game):

	max_players = 2

	def __init__(self, opts, players, player_names, map_path="", teams=[]):
		#self.opts = opts
		self.gamename = "PlanetWars"
		if map_path == "":
			self.map_path = test_map_path
			turns = 10
		else:
			self.map_path = map_path
			turns = 200
		self.opts = {
			'turns':turns,	
			'loadtime': 5000,
			'turntime': 1000,
			'cutoff_percent': 0.85,
			'cutoff_turn': 150,
			'secure_jail' : True,
			'capture_errors' : True,
			'players' : 2,
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
		game = planetwars.PlanetWars(self.opts)
		game_result = engine.run_game(game, self.players, self.opts)
		game_result['playernames'] = self.player_names
		if 'replaydata' in game_result:
			game_result['replaydata']['player_one'] = self.player_names[0]
			game_result['replaydata']['player_two'] = self.player_names[1]
			game_result['replaydata']['playernames'] = self.player_names
		print(game_result)
		return game_result

 
Game = PlanetWars

