#!/usr/bin/env python
#
# usage: bin/run-tron-game.py -p -v -z ../bot1/MyBot.py ../bot2/MyBot.py
#
# i.e. you need to be in the aiweb root directory for the script to work

import argparse, json, os, sys

sys.path.append("web")

from aiweb_tools import config
from aiweb_tools import games
from aiweb_tools.games import engine
from aiweb_tools.games.tron_game import tron

test_map_path = "../maps/test_map.map"


parser = argparse.ArgumentParser(description='Run Tron game locally.')
parser.add_argument("BOT1", help="path to bot program")
parser.add_argument("BOT2", help="path to bot program")
parser.add_argument("-m", "--map", help="map to play the game on", default="../maps/test_map.map")
parser.add_argument("-p", "--print_replay", help="print replay JSON", action="store_true")
parser.add_argument("-t", "--turns", help="max number of turns to play", type=int, default=1000)
parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
parser.add_argument("-z", "--visualize", help="write replay.html", action="store_true")
args = parser.parse_args()


class Tron(games.Game):
	max_players = 2

	def __init__(self, args):
		self.gamename = "Tron"
		self.map_path = args.map
		turns = args.turns
		if args.verbose:
			verbose = sys.stderr
		else:
			verbose = None
		self.opts = {
			'turns'             : turns,
			'loadtime'          : 5000,
			'turntime'          :  500,
			'cutoff_percent'    :    0.85,
			'cutoff_turn'       :  150,
			'kill_points'       :    2,
			'secure_jail'       : False,
			'capture_errors'    : True,
			'agents_per_player' :    1,
			#'error_log'         : sys.stderr,
			#'input_log'         : sys.stderr,
			#'output_log'        : sys.stderr,
			#'replay_log'        : sys.stderr,
			#'stream_log'        : sys.stderr,
			'verbose_log'       : verbose,
		}
		self.players = [[os.path.dirname(args.BOT1), args.BOT1], [os.path.dirname(args.BOT2), args.BOT2]]
		self.player_names = [os.path.basename(args.BOT1), os.path.basename(args.BOT2)]

	def run_game(self):
		if self.opts.get('verbose_log', None):
			self.opts['verbose_log'].write("map path: " + str(self.map_path) + "\n")
		with open(self.map_path) as fo:
			map_text = "".join(fo.readlines())
		self.opts['map'] = map_text
		game = tron.Tron(self.opts)
		game_result = engine.run_game(game, self.players, self.opts)
		game_result['playernames'] = self.player_names
		return game_result


game = Tron(args)
result = game.run_game()

if args.print_replay:
	print result["replaydata"]

if args.visualize:
	# I did not want to require Django to just use its templates.
	with open ("resources/replay-template-tron.html", "r") as myfile:
		template = myfile.read()
	with open ("replay.html", "w") as myfile:
		myfile.write(template % json.dumps(result['replaydata']))
