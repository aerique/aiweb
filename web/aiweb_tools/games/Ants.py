from aiweb_tools.games import engine
from aiweb_tools.games.ants_game import ants

class Ants(aiweb_tools.games.Game):
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
 
Game = Ants
