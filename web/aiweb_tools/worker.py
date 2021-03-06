#   Copyright 2016 The aichallenge Community
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import uuid
import datetime
import subprocess
import glob
import os.path
import time
import shutil
import cloudpickle

#from .. import config
from aiweb_tools import config
import aiweb_tools.zeta.submission
from aiweb_tools import comms
import aiweb_tools.match

from aiweb_tools import games

from aiweb_tools.games import engine

my_ip = "127.0.0.1" # Change this for each server running workers, unless using a single-server install for all parts including webserver
#worker_temp = "/home/" + config.task_username + "/aiweb/worker_tmp/"

class Worker:
	""" Workers are responsible for compiling submissions and running matches """
	def __init__(self):
		self.uuid = uuid.uuid4()

	def task_request_content(self):
		""" Content of a task request file for this worker """
		content = my_ip + "\n" + self.uuid.hex
		return content

	def request_task(self):
		""" Send a task request to the task server"""
		print("Requesting task")
		srcname = "worker-ready" + config.delimiter + (datetime.datetime.now().isoformat()).replace(":", "-") + config.delimiter + self.uuid.hex
		f = open(srcname, 'w')
		f.write(self.task_request_content())
		f.close()
		comms.send_task_worker_ip (srcname, config.task_ip)

		comms.delete_file(srcname)
		

	def await_task(self):
		""" Wait for a task and complete it if appropriate """
		stopfile = (config.task_worker_path + "stop" + config.delimiter + self.uuid.hex) 
		while not os.path.isfile(stopfile):
			ready = ".ready"
			for file in glob.glob(config.task_worker_path + "*" + ready):
#				print(file)
				real = (file[:-len(ready)])
				prefix = file.split('/')[-1]
				if (prefix.startswith("worker-ready")):
					pass
				else:
					if (self.task_is_mine(real)):
						self.do_task(real)
						comms.delete_file(real)
						comms.delete_file(file)
					else:
						lockfile = file + ".lock"
						try:
							with open(lockfile, 'x') as fo:
								self.do_task(real)
								comms.delete_file(real)
								comms.delete_file(file)
							comms.delete_file(lockfile)
						except OSError as e:
							pass
					
			time.sleep(config.sleeptime)
			self.request_task()

			print("checking for tasks")

		comms.delete_file(stopfile)

		
	def task_is_mine(self, taskfile):
		""" Check if the task is mine or not """
		fname = taskfile.split("/")[-1]
		if fname.startswith("compile"):
			with open(taskfile) as fo:
				line = fo.readline().strip()
				return line.endswith(self.uuid.hex)
		elif fname.startswith("match" + config.delimiter):
			stripped = fname.strip("match" + config.delimiter)
			return stripped.startswith(self.uuid.hex)

	def do_task(self, taskfile):
		""" Do the task found in taskfile """
		print("doing task: " + taskfile)
		fname = taskfile.split("/")[-1]
		if fname.startswith("compile"):
			with open(taskfile) as fo:
				line = fo.readline().strip().split(" ")
				if len(line) < 2:
					print("Error: compile task file should have at least 2 columns")
					pass
				else:
					if line[0] == "compile":
						self.compile(line[1])
		elif fname.startswith("match"):
			match = aiweb_tools.match.Match()
			match.read(taskfile)
			print("Running match: " + str(match))
			self.run_match(match)

	def compile(self, subm_id):
		""" Compile the named submission """
		print("compiling: " + subm_id)
		if not os.path.isfile(config.datastore_submission_path + subm_id):
			comms.get_submission(config.datastore_submission_path + subm_id)
		path = self.compiled_bot_path(subm_id)
		if not os.path.exists(path):
			os.makedirs(path)
			target = (path )#+ "compile/")
			subprocess.call(["unzip", config.datastore_submission_path + subm_id, "-d", target])
	
			subm_data = subm_id.split(config.delimiter)
			username = subm_data[0]
			game_id = subm_data[1]
			print("username" + username)
			subm = aiweb_tools.zeta.submission.Submission(username, subm_id, target)
			print("Compiling")
			subm.compile()
			print("Running functional test")
			if subm.compile_success():
				self.functional_test(game_id, subm)
				print("finished functional test")
			else:
				print("Not testing because compile failed")
			self.send_compile_result(path, subm_id, game_id, subm)

	def functional_test(self, gamename, submission):
		""" Run a test game for submission to see if it crashes """
		game_class = games.get_game(gamename)
		players = [(submission.directory, submission.get_command(config.worker_compiled + submission.sub_id))] * 2
		print(players)
#		players = self.get_bot_commands([submission.sub_id, submission.sub_id])
		game = game_class(None, players, [submission.username, submission.username])
		result = game.run_game()
		if 'status' in result:
			if result['status'][0] in ('crashed', 'timeout', 'invalid'):
				submission.set_test_status(False, result['status'][0] + "\n" + result['errors'][0])
			else:
				submission.set_test_status(True)
		else:
			print("status not in result:")
			print (str(result))
				
		

	def save_report(self, submission, path):
		""" Save a submission report located at path """
		lang = ""
		if not (submission.language == None):
			lang = submission.language
		content = submission.vshort_message() + "\n" + lang + "\n" + submission.full_report()
		with open(path, 'w') as fo:
			fo.write(content)

	def send_compile_result(self, path, subm_id, game_id, submission):
		""" send results of compilation back to webserver """
		runfile = path + "run_command"
		if os.path.exists(runfile):	# make sure they don't put malicious commands in here, by deleting the file if it exists
			subprocess.call(["chmod", "u+rw", runfile])
			subprocess.call("rm", "-f", runfile)
		with open(runfile, 'wb') as fo:
			cloudpickle.dump(submission, fo)
		subprocess.call(["chmod", "u+r", path + "*"])
		zipfile = path + subm_id + "-compiled.zip"
		subprocess.call(["zip", "-r", zipfile, path, "-i", path + "*"])
		comms.send_file_datastore_ready(zipfile, config.datastore_submission_path)
		reportfile = path + subm_id + "-report.txt" 
		self.save_report(submission, reportfile)
		comms.send_file_webserver_ready(reportfile, config.webserver_results_path)
		if (submission.is_ready()):
			self.send_matchmaker_compile_info(path, submission.username, game_id, subm_id)

	def send_matchmaker_compile_info(self, path, username, game_id, submission_id):
		""" Send relevant compile info to matchmaker """
		filepath = path + "compiled" + config.delimiter + submission_id
		content = username + "\n" + game_id + "\n" + submission_id + "\n"
		with open (filepath, 'w') as fo:
			fo.write(content)
		comms.send_file_matchmaker_ready(filepath, config.matchmaker_path)

	def compiled_bot_path(self, bot):
		""" Get the path for the compiled bot """
		return config.worker_compiled + bot + "/"

	def get_compiled_bot(self, bot):
		""" Download and unzip the named compiled bot """
		path = self.compiled_bot_path(bot)
		os.mkdir(path)

		zipfile = bot + "-compiled.zip"
		comms.get_submission_from_filename(zipfile)
		subprocess.call(["unzip", "-j", "-o", config.datastore_submission_path + zipfile, "-d", path])

	def get_bot_command(self, bot):
		""" Get the command to run bot
		(also get the bot if not present FIXME function name) """
		print(bot)
		path = self.compiled_bot_path(bot)
		if not os.path.exists(path):
			self.get_compiled_bot(bot)
		run_command = self.get_run_command(path + "run_command")
		print(run_command)
		return (path, run_command)

	def get_run_command(self, filepath):
		""" Load the submission object and get the command to run
		the compiled bot """
		with open (filepath, 'rb') as fo:
			subm = cloudpickle.load(fo)
			return subm.get_command(config.worker_compiled + subm.sub_id)

	def get_bot_commands(self, bots):
		""" Get the commands to run listed bots """
		print("Bot commands:")
		return [self.get_bot_command(bot) for bot in bots]

	def get_player_name(self, bot):
		""" Get the name of the player who owns bot """
		return bot.split(config.delimiter)[0]

	def run_match(self, match):
		""" run specified match """
		players = self.get_bot_commands(match.bots)
		player_names = [self.get_player_name(player) for player in match.bots]
		game_class = games.get_game(match.gamename)
		game = game_class(None, players, player_names, match.map_file)
		result = game.run_game()
		comms.send_result(match, result)

class Worker_data:
	#FIXME just pickle the data instead
	uuid = ""
	ip_addr = ""
	def write(self, filepath):
		with open(filepath, 'w') as fo:
			fo.write(self.ip_addr)
			fo.write(self.uuid)
	def read(self, filepath):
		with open(filepath) as fo:
			self.ip_addr = fo.readline().strip()
			self.uuid = fo.readline().strip()

