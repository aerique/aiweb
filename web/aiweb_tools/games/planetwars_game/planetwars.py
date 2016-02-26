#!/usr/bin/env python3

from random import randrange, choice, shuffle, randint, seed, random
from math import cos, pi, sin, sqrt, atan
from collections import deque, defaultdict

from fractions import Fraction
import operator
from .game import Game
from copy import deepcopy

from . import original

try:
	from sys import maxint
except ImportError:
	from sys import maxsize as maxint

LAND = -2
WATER = -1
MAP_OBJECT = '.%'

HEADING = {'n' : (-1, 0),
		   'e': (0, 1),
		   's': (1, 0),
		   'w': (0, -1)}

class PlanetWars(Game):
	def __init__(self, options=None):
		# setup options
		self.cutoff = None
		map_text = options['map']
		self.turns = int(options['turns'])
		self.loadtime = int(options['loadtime'])
		self.turntime = int(options['turntime'])
		self.engine_seed = options.get('engine_seed',
									   randint(-maxint-1, maxint))
		self.player_seed = options.get('player_seed',
									   randint(-maxint-1, maxint))

		seed(self.engine_seed)
		map_data = self.parse_map(map_text)
		self.planets = map_data['planets']
		self.fleets = map_data['fleets']
		self.temp_fleets = []

		self.turn = 0
		self.num_players = map_data["players"]
		self.player_to_begin = randint(0, self.num_players)
		# used to cutoff games early
		self.cutoff_turns = 0
		# used to calculate the turn when the winner took the lead
		self.winning_bot = None
		self.winning_turn = 0
		# used to calculate when the player rank last changed
		self.ranking_bots = None
		self.ranking_turn = 0

		# initialize scores
		self.score = [0]*self.num_players
		self.bonus = [0]*self.num_players
		self.score_history = [[s] for s in self.score]

		# cache used by neighbourhood_offsets() to determine nearby squares
		self.offsets_cache = {}

		# used to track dead players, ants may still exist, but orders are not processed # Ants?
		self.killed = [False for _ in range(self.num_players)]

		# used to give a different ordering of players to each player;
		# initialized to ensure that each player thinks they are player 0
	# Not actually used here, see the mechanism in original.py
		self.switch = [[None]*self.num_players + list(range(-5,0))
					   for i in range(self.num_players)]
		for i in range(self.num_players):
			self.switch[i][i] = 0

		# the engine may kill players before the game starts and this is needed
		# to prevent errors
		self.orders = [[] for i in range(self.num_players)]

		### collect turns for the replay
		self.replay_data = []


	def parse_map(self, map_text):
		
		""" Parse the map_text into a more friendly data structure """
		planets, fleets = original.read_map_file(map_text)
		return {
			"planets": planets,
			"fleets": fleets,
			"players": 2,
		}

	def render_changes(self, player):
		""" Create a string which communicates the updates to the state
		"""
		message = original.serialize_game_state(self.planets, self.fleets, player)
		return message
		

	def get_state_changes(self):
		""" Return a list of all transient objects on the map.

			Changes are sorted so that the same state will result in the same
			output.
		"""
		changes = []
		changes.extend(sorted(
			['P', a["x"], a["y"], a["owner"], str(int(a["num_ships"])), str(int(a["growth_rate"]))]
			for a in self.planets))
		changes.extend(sorted(
			['F', f["owner"], str(int(f["num_ships"])), str(int(f["source"])), str(int(f["destination"])), str(int(f["total_trip_length"])), str(int(f["turns_remaining"]))]
			for f in self.fleets))
		return changes

	def parse_orders(self, player, lines):
		""" Parse orders from the given player

			Orders must be of the form: o row col heading
			row and col refer to the location of the agent you are ordering.
		"""
		orders = []
		valid = []
		ignored = []
		invalid = []

		for line in lines:
			line = line.strip().lower()
			# ignore blank lines and comments
			if not line: # or line[0] == '#':
				continue

			if line[0] == '#':
				ignored.append((line))
				continue

			order = original.parse_order_string(line)


			# if all is well, append to orders
			if not (order == None):
				orders.append((player, row, col, heading))
				valid.append(line)
			else:
				invalid.append(line)

		return orders, valid, ignored, invalid

#	def validate_orders(self, player, orders, lines, ignored, invalid):
#		""" Validate orders from a given player
#
#			Location (row, col) must be ant belonging to the player
#			direction must not be blocked
#			Can't multiple orders to one ant
#		"""
#		valid = []
#		valid_orders = []
#		seen_locations = set()
#		for line, (player, row, col, heading) in zip(lines, orders):
#			if not self.player_has_agent(player, row, col):
#				invalid.append((line,'no agent belonging to this player at this location'))
#				continue
#			if row < 0 or col < 0:
#				invalid.append((line,'out of bounds'))
#				continue
#
#			# this order is valid!
#			valid_orders.append((player, row, col, heading))
#			valid.append(line)
#
#		return valid_orders, valid, ignored, invalid


#	def update_move_sequence(self):
#		self.player_to_begin = self.player_to_begin + 1
#		if self.player_to_begin >= self.num_players:
#			self.player_to_begin = self.player_to_begin - self.num_players

#	def get_move_sequence(self):
#		""" Sequence for cycling through players so they all sometimes 
#			get to move first
#		"""
#		p1 = range(self.player_to_begin, self.num_players)
#		result = p1 + (range(0, self.player_to_begin))
#		return result

#	def do_move_phase_order(self, dtuple):
#		(player, action, num, source, target) = dtuple
#		valid = False
#		if action == "d": pass
#		elif action == "a":
#			if self.territory[target]["owner"] != player and num > 0 and self.territory[source]["owner"] == player and self.territory[source]["armies"] > 1:
#				valid = True
#				will_send = min (num, (self.territory[source]["armies"] - 1))
#				self.attack (player, num, source, target)
#		elif action == "t":
#			if self.territory[target]["owner"] == player and self.territory[source]["owner"] == player and num > 0 and self.territory[source]["armies"] > 1:
#				valid = True
#				will_send = min (num, (self.territory[source]["armies"] - 1))
#				self.transfer (player, num, source, target)
#		elif action == "m":
#			if num > 0 and self.territory[source]["armies"] > 1:
#				if self.territory[source]["owner"] == player:
#					valid = True
#					will_send = min (num, (self.territory[source]["armies"] - 1))
#					if self.territory[target]["owner"] == player:
#						self.transfer (player, will_send, source, target)
#					else:
#						self.attack (player, will_send, source, target)
#		return valid

#	def process_next_order(self, player):
#		""" Process one player order in which something actually happens
#		"""
#		if not player["finished_turn"]:
#			done = False
#			while not done:
#				if len(self.orders[player]) <= player["move_index"]:
#					player["finished_turn"] = True
#					done = True
#				else:
#					order = self.orders[player][player["move_index"]]
#					valid = self.do_move_phase_order(order)
#					player["move_index"] += 1
#					if valid:
#						done = True


#	def destination(self, loc, d):
#		""" Returns the location produced by offsetting loc by d """
#		return ((loc[0] + d[0]) % self.rows, (loc[1] + d[1]) % self.cols)
#
#	def tron_orders(self, player):
#		""" Enacts orders for the Tron game
#		"""
#		player_orders = self.orders[player]
#		done = False
#		for order in player_orders:
#			if not done:
#				(player_id, row, col, heading) = order
#				for agent in self.agents:
#					if agent["row"] == row and agent["col"] == col and agent["owner"] == player_id:
#						agent["heading"] = heading
#
#
#	def pre_move_agents(self):
#		""" Process the portion of the agent's move which should take
#			place before the agent's location and map obstacles are updated.
#		"""
#		for agent in self.agents:
#			row, col = agent["row"], agent["col"]
#			heading = agent["heading"]
#			dest = self.destination([row, col], HEADING[heading])
#			if not self.grid[dest[0]][dest[1]] == LAND:
#				self.killed_agent_locations.append([dest, agent["owner"]])
#			else: self.agent_destinations.append([dest, agent["owner"]])
#
#	def kill_overlap(self):
#		""" Kills agents who step onto the same square in the same turn
#		"""
#		unique = []
#		for value in self.agent_destinations:
#			location, owner = value
#			if not location in unique:
#				unique.append(location)
#			else:
#				self.killed_agent_locations.append(value)
#
#	def mark_trail(self):
#		""" Mark trails as obstacles on the map
#		"""
#		for (row, col), owner in self.agent_destinations:
#			self.grid[row][col] = owner
#
#	def update_scores_for_agent_demise(self):
#		""" When an agent dies, its owner loses a point and everybody else
#			alive at the start of this turn gains one
#		"""
#		for agent in self.agents:
#			if (agent["row"], agent["col"]) in [(r, c) for (r, c), _ in self.killed_agent_locations]:
#				for count in range(self.num_players):
#					if count == agent["owner"]:
#						self.score[count] -= 1
#					elif self.is_alive(count):
#						self.score[count] +=1  

#	def remove_killed(self):
#		""" Remove dead agents from the list of active ones
#		"""
#		remaining = []
#		for agent in self.agents:
#			if (agent["row"], agent["col"]) in [(r, c) for (r, c), _ in self.killed_agent_locations]:
#				self.killed_agents.append(agent)
#			else:
#				remaining.append(agent)
#		self.agents = remaining
#
#	def update_agents(self):
#		""" Update the agent's location in preparation for next turn
#		"""
#		for agent in self.agents:
#			row, col = agent["row"], agent["col"]
#			heading = agent["heading"]
#			dest_row, dest_col = self.destination([row, col], HEADING[heading])
#			agent["row"] = dest_row
#			agent["col"] = dest_col

	def pw_orders(self, player):
		""" Enacts orders for the PlanetWars game
		"""
		player_orders = self.orders[player]
		print("player_orders" + str(player_orders))
		done = False
		for order in player_orders:
			if not done:
				porder = original.parse_order(order)
				if not original.issue_order(porder, player, self.planets, self.fleets, self.temp_fleets):
					self.replay_data.append("Bad order: " + str(order))
					

	def do_orders(self):
		""" Execute player orders and handle conflicts
		"""
		for player in range(self.num_players):
			if self.is_alive(player):
				self.pw_orders(player)
			else:
				print("Player dead: " + player)
#			else: self.killed[player] == True
#		self.pre_move_agents()
#		self.kill_overlap()
#		self.update_agents()
#		self.update_scores_for_agent_demise()
#		self.remove_killed()
#		self.mark_trail()

#	def remaining_players(self):
#		""" Return the players still alive """
#		return [p for p in range(self.num_players) if self.is_alive(p)]

	# Common functions for all games

	def game_over(self):
		""" Determine if the game is over

			Used by the engine to determine when to finish the game.
			A game is over when there are no players remaining, or a single
			  winner remaining.
		"""
		if len(self.remaining_players()) < 1:
			self.cutoff = 'extermination'
			return True
		elif len(self.remaining_players()) == 1:
			self.cutoff = 'lone survivor'
			return True
		else: return False

	def kill_player(self, player):
		""" Used by engine to signal that a player is out of the game """
		self.killed[player] = True

	def start_game(self):
		""" Called by engine at the start of the game """
		self.game_started = True
		
		### append turn 0 to replay
		self.replay_data.append( self.get_state_changes() )
		result = []

	def finish_game(self):
		""" Called by engine at the end of the game """

		self.calc_significant_turns()
		for i, s in enumerate(self.score):
			self.score_history[i].append(s)
		self.replay_data.append( self.get_state_changes() )

		# check if a rule change lengthens games needlessly
		if self.cutoff is None:
			self.cutoff = 'turn limit reached'

	def start_turn(self):
		""" Called by engine at the start of the turn """
		self.turn += 1
		self.orders = [[] for _ in range(self.num_players)]
		self.temp_fleets = {}

	def finish_turn(self):
		""" Called by engine at the end of the turn """
		self.do_orders()
		original.process_new_fleets(self.planets, self.fleets, self.temp_fleets)
		self.planets, self.fleets = original.do_time_step(self.planets, self.fleets)
		print(self.fleets)
		# record score in score history
		for i, s in enumerate(self.score):
			if self.is_alive(i):
				self.score_history[i].append(s)
			elif s != self.score_history[i][-1]:
				# score has changed, increase history length to proper amount
				last_score = self.score_history[i][-1]
				score_len = len(self.score_history[i])
				self.score_history[i].extend([last_score]*(self.turn-score_len))
				self.score_history[i].append(s)
		self.calc_significant_turns()
#		self.update_scores()

		### append turn to replay
		self.replay_data.append( self.get_state_changes() )

	def calc_significant_turns(self):
		ranking_bots = [sorted(self.score, reverse=True).index(x) for x in self.score]
		if self.ranking_bots != ranking_bots:
			self.ranking_turn = self.turn
		self.ranking_bots = ranking_bots

		winning_bot = [p for p in range(len(self.score)) if self.score[p] == max(self.score)]
		if self.winning_bot != winning_bot:
			self.winning_turn = self.turn
		self.winning_bot = winning_bot

	def get_state(self):
		""" Get all state changes

			Used by engine for streaming playback
		"""
		updates = self.get_state_changes()
		updates.append([]) # newline
		return '\n'.join(' '.join(map(str,s)) for s in updates)

	def get_player_start(self, player=None):
		""" Get game parameters visible to players

			Used by engine to send bots startup info on turn 0
		"""
		result = []
		result.append(['turn', 0])
		result.append(['loadtime', self.loadtime])
		result.append(['turntime', self.turntime])
		result.append(['player_id', player])
		result.append(['turns', self.turns])
		result.append(['player_seed', self.player_seed])
		result.append(['num_players', self.num_players])
		message = self.get_player_state(player)

		result.append([]) # newline
		pen = '\n'.join(' '.join(map(str,s)) for s in result)
		return pen + message

	def get_player_state(self, player):
		""" Get state changes visible to player

			Used by engine to send state to bots
		"""
		return self.render_changes(player)

	def is_alive(self, player):
		""" Determine if player is still alive

			Used by engine to determine players still in the game
		"""
		if self.killed[player]:
			return False
		else:
			return True

	def get_error(self, player):
		""" Returns the reason a player was killed

			Used by engine to report the error that kicked a player
			  from the game
		"""
		return ''

	def do_moves(self, player, moves):
		""" Called by engine to give latest player orders """
		orders, valid, ignored, invalid = self.parse_orders(player, moves)
#		orders, valid, ignored, invalid = self.validate_orders(player, orders, valid, ignored, invalid)
		self.orders[player] = orders
		print("do_moves called: " + str(orders))
		return valid, ['%s # %s' % ignore for ignore in ignored], ['%s # %s' % error for error in invalid]

	def get_scores(self, player=None):
		""" Gets the scores of all players

			Used by engine for ranking
		"""
		if player is None:
			return self.score
		else:
			return self.order_for_player(player, self.score)

	def order_for_player(self, player, data):
		""" Orders a list of items for a players perspective of player #

			Used by engine for ending bot states
		"""
		s = self.switch[player]
		return [None if i not in s else data[s.index(i)]
				for i in range(max(len(data),self.num_players))]

	def remaining_players(self):
		""" Return the players still alive """
		return [p for p in range(self.num_players) if self.is_alive(p)]

	def get_stats(self):
		"""  Used by engine to report stats
		"""
		stats = {}
		return stats

	def get_replay(self):
		""" Return a summary of the entire game

			Used by the engine to create a replay file which may be used
			to replay the game.
		"""
		replay = {}
		# required params
		replay['revision'] = 1
		replay['players'] = self.num_players

		# optional params
		replay['loadtime'] = self.loadtime
		replay['turntime'] = self.turntime
		replay['turns'] = self.turns
		replay['engine_seed'] = self.engine_seed
		replay['player_seed'] = self.player_seed

		# scores
		replay['scores'] = self.score_history
		replay['bonus'] = self.bonus
		replay['winning_turn'] = self.winning_turn
		replay['ranking_turn'] = self.ranking_turn
		replay['cutoff'] =  self.cutoff

		replay['planets'] = self.planets
		replay['fleets'] = self.fleets

		
		### 
		replay['data'] = self.replay_data
		return replay
