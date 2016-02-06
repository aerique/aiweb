#!/usr/bin/env python2

from random import randrange, choice, shuffle, randint, seed, random
from math import cos, pi, sin, sqrt, atan
from collections import deque, defaultdict

from fractions import Fraction
import operator
from .game import Game
from copy import deepcopy
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

class Tron(Game):
    def __init__(self, options=None):
        # setup options
        map_text = options['map']
        self.turns = int(options['turns'])
        self.loadtime = int(options['loadtime'])
        self.turntime = int(options['turntime'])
        self.engine_seed = options.get('engine_seed',
                                       randint(-maxint-1, maxint))
        self.player_seed = options.get('player_seed',
                                       randint(-maxint-1, maxint))
        seed(self.engine_seed)

        self.cutoff_percent = options.get('cutoff_percent', 0.85)
        self.cutoff_turn = options.get('cutoff_turn', 150)

        self.scenario = options.get('scenario', False)

        map_data = self.parse_map(map_text)

#        self.group_count = self.count_groups(map_data)

        self.turn = 0
        self.num_players = map_data["players"]
        self.agents_per_player = map_data["agents_per_player"]
        self.player_to_begin = randint(0, self.num_players)
        # used to cutoff games early
        self.cutoff = None
        self.cutoff_bot = None # Can be ant owner, FOOD or LAND
        self.cutoff_turns = 0
        # used to calculate the turn when the winner took the lead
        self.winning_bot = None
        self.winning_turn = 0
        # used to calculate when the player rank last changed
        self.ranking_bots = None
        self.ranking_turn = 0

        # initialize size
        self.rows, self.cols = map_data['size']

        # for scenarios, the map file is followed exactly
#This might be Ants-specific and removeable?
        if self.scenario:
            # initialize ants
            #for player, player_ants in map_data['ants'].items():
            #    for ant_loc in player_ants:
            #        self.add_initial_ant(ant_loc, player)
            self.original_map = []
            for map_row in self.map:
                self.original_map.append(map_row[:])

        # initialize scores
        self.score = [self.agents_per_player]*self.num_players
        self.bonus = [0]*self.num_players
        self.score_history = [[s] for s in self.score]

        # cache used by neighbourhood_offsets() to determine nearby squares
        self.offsets_cache = {}

        # used to track dead players, ants may still exist, but orders are not processed
        self.killed = [False for _ in range(self.num_players)]

        # used to give a different ordering of players to each player;
        # initialized to ensure that each player thinks they are player 0
        self.switch = [[None]*self.num_players + list(range(-5,0))
                       for i in range(self.num_players)]
        for i in range(self.num_players):
            self.switch[i][i] = 0

        # the engine may kill players before the game starts and this is needed
        # to prevent errors
        self.orders = [[] for i in range(self.num_players)]
        self.agent_destination = []
        self.killed_agent_locations = []
        self.killed_agents = []
        self.agents = deepcopy(map_data["agents"])
        self.water = deepcopy(map_data["water"])

        self.grid = self.make_grid()
        self.verify_agent_starting_locations()
#        raise Exception(self.grid)
        ### collect turns for the replay
        self.replay_data = []

    def make_grid(self):
        """ Called to build the map grid and mark initial obstacles
        """
        grid = []
        for count_row in range(self.rows):
            new_row = []
            for count_col in range(self.cols):
                new_row.append(LAND)
            grid.append(new_row)
        for (row, col) in self.water:
            try:
                grid[row][col] = WATER
            except IndexError:
                raise Exception("row, col outside range ", row, col, grid)
        for agent in self.agents:
            grid[agent["row"]][agent["col"]] = agent["owner"]
        return grid

    def player_has_agent(self, player, row, col):
        result = False
        for agent in self.agents:
            if agent["owner"] == player and agent["row"] == row and agent["col"] == col:
                result = True
        return result

    def verify_agent_starting_locations(self):
        for agent in self.agents:
            row, col = agent["row"], agent["col"]
            if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
                raise Exception("Agent at {0}, {1} is out of bounds".format(row, col))

    def parse_map(self, map_text):
        """ Parse the map_text into a more friendly data structure """
        cols = None
        rows = None
        agents_per_player = None
        agents = []
        water = []
        num_players = None
        count_row = 0

        for line in map_text.split("\n"):
            line = line.strip()

            # ignore blank lines and comments
            if not line or line[0] == "#":
                continue

            key, value = line.split(" ", 1)
            key = key.lower()

            if key == "cols":
                cols = int(value)
            elif key == "rows":
                rows = int(value)
            elif key == "players":
                num_players = int(value)
            elif key == "agents_per_player":
                agents_per_player = int(value)
            elif key == "a":
                values = value.split()
                row = int(values[0])
                col = int(values[1])
                heading = (values[2])
                owner = int(values[3])
                agents.append({"owner": owner,
                               "row" : row,
                               "col" : col,
                               "heading": heading})
            elif key == 'm':
                if num_players is None:
                    raise Exception("map",
                                    "players count expected before map lines")
                if len(value) != cols:
                    raise Exception("map",
                                    "Incorrect number of cols in row %s. "
                                    "Got %s, expected %s."
                                    %(row, len(value), width))
                for count_col, c in enumerate(value):
                    if c == MAP_OBJECT[WATER]:
                        water.append((count_row, count_col))
                    elif c != MAP_OBJECT[LAND]:
                        raise Exception("map",
                                        "Invalid character in map: %s" % c)
                count_row += 1
        if count_row != rows:
                    raise Exception("map",
                                    "Incorrect number of rows in map "
                                    "Got %s, expected %s."
                                    %(count_row, rows))
        return {
            "size": (rows, cols),
            "agents_per_player": agents_per_player,
            "agents": agents,
            "players": num_players,
            "water": water }

    def render_changes(self, player):
        """ Create a string which communicates the updates to the state
        """
        updates = self.get_state_changes()
        visible_updates = []
        # next list all transient objects
        for update in updates:
            visible_updates.append(update)
        visible_updates.append([]) # newline
        return '\n'.join(' '.join(map(str,s)) for s in visible_updates)

    def get_state_changes(self):
        """ Return a list of all transient objects on the map.

            Changes are sorted so that the same state will result in the same
            output.
        """
        changes = []
#        changes.extend(sorted(
#            ['p', p["player_id"]]
#            for p in self.players if self.is_alive(p["player_id"])))
        changes.extend(sorted(
            ['a', a["row"], a["col"], a["heading"], a["owner"]]
            for a in self.agents))
        changes.extend(sorted(
            ['d', a["row"], a["col"], a["heading"], a["owner"]]
            for a in self.killed_agents))
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

            data = line.split()

            # validate data format
            if data[0] != 'o':
                invalid.append((line, 'unknown action'))
                continue
            else:
                row, col, heading = data[1:]

            # validate the data types
            try:
                row, col = int(row), int(col)
            except ValueError:
                invalid.append((line, "row and col should be integers"))
                continue
            if heading not in HEADING:
                invalid.append((line, "invalid direction"))
                continue

            # if all is well, append to orders
            orders.append((player, row, col, heading))
            valid.append(line)

        return orders, valid, ignored, invalid

    def validate_orders(self, player, orders, lines, ignored, invalid):
        """ Validate orders from a given player

            Location (row, col) must be ant belonging to the player
            direction must not be blocked
            Can't multiple orders to one ant
        """
        valid = []
        valid_orders = []
        seen_locations = set()
        for line, (player, row, col, heading) in zip(lines, orders):
            ## validate orders
            #if loc in seen_locations:
            #    invalid.append((line,'duplicate order'))
            #    continue
            if not self.player_has_agent(player, row, col):
                invalid.append((line,'no agent belonging to this player at this location'))
                continue
#            try:
#                test_loc = 
#            except IndexError:
#                invalid.append((line,'out of bounds'))
#                continue
            if row < 0 or col < 0:
                invalid.append((line,'out of bounds'))
                continue

            # this order is valid!
            valid_orders.append((player, row, col, heading))
            valid.append(line)
            #seen_locations.add(loc)

        return valid_orders, valid, ignored, invalid

#    def max_orders(self):
#        result = 0
#        for player_orders in self.orders:
#            if len(player_orders) > result:
#                result = len(player_orders)
#        return result

    def update_move_sequence(self):
        self.player_to_begin = self.player_to_begin + 1
        if self.player_to_begin >= self.num_players:
            self.player_to_begin = self.player_to_begin - self.num_players

    def get_move_sequence(self):
        """ Sequence for cycling through players so they all sometimes 
            get to move first
        """
        p1 = range(self.player_to_begin, self.num_players)
        result = p1 + (range(0, self.player_to_begin))
        return result

    def do_move_phase_order(self, dtuple):
        (player, action, num, source, target) = dtuple
        valid = False
        if action == "d": pass
        elif action == "a":
            if self.territory[target]["owner"] != player and num > 0 and self.territory[source]["owner"] == player and self.territory[source]["armies"] > 1:
                valid = True
                will_send = min (num, (self.territory[source]["armies"] - 1))
                self.attack (player, num, source, target)
        elif action == "t":
            if self.territory[target]["owner"] == player and self.territory[source]["owner"] == player and num > 0 and self.territory[source]["armies"] > 1:
                valid = True
                will_send = min (num, (self.territory[source]["armies"] - 1))
                self.transfer (player, num, source, target)
        elif action == "m":
            if num > 0 and self.territory[source]["armies"] > 1:
                if self.territory[source]["owner"] == player:
                    valid = True
                    will_send = min (num, (self.territory[source]["armies"] - 1))
                    if self.territory[target]["owner"] == player:
                        self.transfer (player, will_send, source, target)
                    else:
                        self.attack (player, will_send, source, target)
        return valid

    def process_next_order(self, player):
        """ Process one player order in which something actually happens
        """
        if not player["finished_turn"]:
            done = False
            while not done:
                if len(self.orders[player]) <= player["move_index"]:
                    player["finished_turn"] = True
                    done = True
                else:
                    order = self.orders[player][player["move_index"]]
                    valid = self.do_move_phase_order(order)
                    player["move_index"] += 1
                    if valid:
                        done = True

#    def unprocessed_orders_remain(self):
#        result = False
#        for player in range(self.num_players):
#            if player["finished_turn"] == False:
#                result = True
#        return result

    def destination(self, loc, d):
        """ Returns the location produced by offsetting loc by d """
        return ((loc[0] + d[0]) % self.rows, (loc[1] + d[1]) % self.cols)

    def tron_orders(self, player):
        """ Enacts orders for the Tron game
        """
        player_orders = self.orders[player]
        done = False
        for order in player_orders:
            if not done:
                (player_id, row, col, heading) = order
                for agent in self.agents:
                    if agent["row"] == row and agent["col"] == col and agent["owner"] == player_id:
                        agent["heading"] = heading

#    def unique_location(self, location, unique):
#        result = True
#        for (test_loc, _) in unique:
#            if location == test_loc:
#                result = False
#                break
#        return result

    def pre_move_agents(self):
        """ Process the portion of the agent's move which should take
            place before the agent's location and map obstacles are updated.
        """
        for agent in self.agents:
            row, col = agent["row"], agent["col"]
            heading = agent["heading"]
            dest = self.destination([row, col], HEADING[heading])
            if not self.grid[dest[0]][dest[1]] == LAND:
                self.killed_agent_locations.append([dest, agent["owner"]])
            else: self.agent_destinations.append([dest, agent["owner"]])

    def kill_overlap(self):
        """ Kills agents who step onto the same square in the same turn
        """
        unique = []
        for value in self.agent_destinations:
            location, owner = value
            if not location in unique:
                unique.append(location)
            else:
                self.killed_agent_locations.append(value)

    def mark_trail(self):
        """ Mark trails as obstacles on the map
        """
        for (row, col), owner in self.agent_destinations:
            self.grid[row][col] = owner

    def update_scores_for_agent_demise(self):
        """ When an agent dies, its owner loses a point and everybody else
            alive at the start of this turn gains one
        """
        for agent in self.agents:
            if (agent["row"], agent["col"]) in [(r, c) for (r, c), _ in self.killed_agent_locations]:
                for count in range(self.num_players):
                    if count == agent["owner"]:
                        self.score[count] -= 1
                    elif self.is_alive(count):
                        self.score[count] +=1  

    def remove_killed(self):
        """ Remove dead agents from the list of active ones
        """
        remaining = []
        for agent in self.agents:
            if (agent["row"], agent["col"]) in [(r, c) for (r, c), _ in self.killed_agent_locations]:
                self.killed_agents.append(agent)
            else:
                remaining.append(agent)
        self.agents = remaining

    def update_agents(self):
        """ Update the agent's location in preparation for next turn
        """
        for agent in self.agents:
            row, col = agent["row"], agent["col"]
            heading = agent["heading"]
            dest_row, dest_col = self.destination([row, col], HEADING[heading])
            agent["row"] = dest_row
            agent["col"] = dest_col

    def do_orders(self):
        """ Execute player orders and handle conflicts
        """
        for player in range(self.num_players):
            if self.is_alive(player):
                self.tron_orders(player)
#            else: self.killed[player] == True
        self.pre_move_agents()
        self.kill_overlap()
        self.update_agents()
        self.update_scores_for_agent_demise()
        self.remove_killed()
        self.mark_trail()

    def remaining_players(self):
        """ Return the players still alive """
        return [p for p in range(self.num_players) if self.is_alive(p)]

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
        #if self.cutoff_turns >= self.cutoff_turn:
        #    if self.cutoff_bot == FOOD:
        #        self.cutoff = 'food not being gathered'
        #    else:
        #        self.cutoff = 'ants not razing hills'
        #    return True
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
#        for row, col in self.water:
#            result.append(['w', row, col])
#        result.append([]) # newline
#        self.replay_data.append(result)

    def finish_game(self):
        """ Called by engine at the end of the game """
#        players = self.remaining_players()
#        if len(players) == 1:
#            for player in range(self.num_players):
#                self.score[player] += self.bonus[player]

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
        self.agent_destinations = []
        self.killed_agents = []
        self.killed_agent_locations = []
#        for player in self.players:
#            self.begin_player_turn(player)

#    def update_scores(self):
#        """ Update the record of players' scores
#            Proposed scoring for Tron: 
#                score = friendly agents alive + opposing agents outlived
#        """

    def finish_turn(self):
        """ Called by engine at the end of the turn """
        self.do_orders()
#        self.do_non_player_movement()
#        self.do_collisions()
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
#        self.update_scores()

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
        result.append(['rows', self.rows])
        result.append(['cols', self.cols])
        result.append(['turns', self.turns])
        result.append(['player_seed', self.player_seed])
        result.append(['num_players', self.num_players])
        result.append(['agents_per_player', self.agents_per_player])
        for row, col in self.water:
            result.append(['w', row, col])
#        result.append(['neutral_id', self.neutral_id])
#        result.extend(sorted(
#            ['t', t["territory_id"], t["group"], t["x"], t["y"], t["owner"], t["armies"]]
#            for t in self.territory))
#        result.extend(sorted(
#            ['c', c["a"], c["b"]]
#            for c in self.connection))
        # information hidden from players
        #if player is None:
        #    result.append(['food_start', self.food_start])
        #    for line in self.get_map_output():
        #        result.append(['m',line])
        result.append([]) # newline
        return '\n'.join(' '.join(map(str,s)) for s in result)

    def get_player_state(self, player):
        """ Get state changes visible to player

            Used by engine to send state to bots
        """
        return self.render_changes(player)

    def living_agents(self, player):
        """ Called to determine whether a player has living agents remaining
        """
        count = 0
        for agent in self.agents:
            if agent["owner"] == player:
                count += 1
        return count

    def is_alive(self, player):
        """ Determine if player is still alive

            Used by engine to determine players still in the game
        """
        if self.killed[player] or self.living_agents(player) == 0:
            return False
        else:
            return True
#            result = False
#            for ship in self.players:
#                if ship["player_id"] == player and ship["current_hp"] > 0:
#                    result = True
#                    break
#            return result

    def get_error(self, player):
        """ Returns the reason a player was killed

            Used by engine to report the error that kicked a player
              from the game
        """
        return ''

    def do_moves(self, player, moves):
        """ Called by engine to give latest player orders """
        orders, valid, ignored, invalid = self.parse_orders(player, moves)
        orders, valid, ignored, invalid = self.validate_orders(player, orders, valid, ignored, invalid)
        self.orders[player] = orders
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

    def get_stats(self):
        """  Used by engine to report stats
        """
        stats = {}
#        stats["territory"] = len(self.territory)
#        stats["connection"] = len(self.connection)
#        stats['score'] = self.score
#        stats['s_alive'] = [1 if self.is_alive(player) else 0
#                            for player in range(self.num_players)]
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
        replay['rows'] = self.rows
        replay['cols'] = self.cols

        # scores
        replay['scores'] = self.score_history
        replay['bonus'] = self.bonus
        replay['winning_turn'] = self.winning_turn
        replay['ranking_turn'] = self.ranking_turn
        replay['cutoff'] =  self.cutoff
        
        replay['water'] = self.water
        ### 
        replay['width'] = self.cols
        replay['height'] = self.rows
        replay['data'] = self.replay_data
        return replay
