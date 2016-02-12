import sys
from aiweb_tools import config

def get_game(name):
	"""get the game class from the module requested"""
	full_name = 'aiweb_tools.games.' + name
	__import__(full_name)
	return sys.modules[full_name].Game

class Game:
	
	gamename = "Default_game"
	num_teams = 0
	min_players = 2
	max_players = 2
	teams = []
	players = []
	player_names = []
	map_path = ""
	opts = {}


	def __init__(self, opts, players, player_names, map_path="", teams=[]):
		self.opts = opts
		self.players = players
		self.player_names = player_names
		self.map_path = map_path
		self.teams = teams

	def player_name(self, player):
		return player.split('_')[0] # .split(config.delimiter)[0] ?

	def run_game(self):
		return {}
