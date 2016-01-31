
SD_PER_MOVE, SD_ABSOLUTE, FISCHER = range(3)

class Bot:
	self.username = ""
	self.score = 0
	self.submission_id = ""
	self.submission_timestamp = ""
	self.submission_games_played = 0
	self.runner = None

class Game:
	
	self.gamename = "Default_game"
	self.num_teams = 0
	self.num_players = 2
	self.turn_limit = 200
	self.time_limit = 500
	self.time_type = SD_PER_MOVE
	self.continuous = True	#  bots are kept running between turns
	self.players = []


	def __init__(self, players):
		self.players = players

	def select_players(self, players):
		most_needy = self.
		weighted = self.assign_weights(players)
