import sys

SD_PER_MOVE, SD_ABSOLUTE, FISCHER = range(3)

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
	opts = {}


	def __init__(self, opts, players, teams=[]):
		self.opts = opts
		self.players = players
		self.teams = teams

