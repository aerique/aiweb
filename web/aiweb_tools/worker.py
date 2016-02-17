import uuid
import datetime
import subprocess
import glob
import os.path
import time
import shutil

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
	def __init__(self):
		self.uuid = uuid.uuid4()

	def task_request_content(self):
		content = my_ip + "\n" + self.uuid.hex
		return content

	def request_task(self):
		print("Requesting task")
		srcname = "worker-ready" + config.delimiter + (datetime.datetime.now().isoformat()).replace(":", "-") + config.delimiter + self.uuid.hex
		f = open(srcname, 'w')
		f.write(self.task_request_content())
		f.close()
		subprocess.call(["scp", srcname, config.task_username + "@" + 
			config.task_ip + "://" +
			config.task_worker_path ]);
		ready_filename = srcname + ".ready"

		subprocess.call(["touch", ready_filename])
		subprocess.call(["scp", ready_filename, config.task_username 
			+ "@" + config.task_ip + "://" +
			config.task_worker_path ])
		subprocess.call(["rm", srcname])
		subprocess.call(["rm", ready_filename])
		

	def await_task(self):
		stopfile = (config.task_worker_path + "stop" + config.delimiter + self.uuid.hex) 
		while not os.path.isfile(stopfile):
			ready = ".ready"
			for file in glob.glob(config.task_worker_path + "*" + ready):
				print(file)
				real = (file[:-len(ready)])
				if (self.task_is_mine(real)):
					self.do_task(real)
					subprocess.call(["rm", real])
					subprocess.call(["rm", file])
			time.sleep(config.sleeptime)
			print("checking for tasks")

		subprocess.call(["rm", stopfile])

		
	def task_is_mine(self, taskfile):
		fname = taskfile.split("/")[-1]
		if fname.startswith("compile"):
			with open(taskfile) as fo:
				line = fo.readline().strip()
				return line.endswith(self.uuid.hex)
		elif fname.startswith("match" + config.delimiter):
			stripped = fname.strip("match" + config.delimiter)
			return stripped.startswith(self.uuid.hex)

	def do_task(self, taskfile):
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
		self.request_task()

	def compile(self, subm_id):
		print("compiling: " + subm_id)
		if not os.path.isfile(config.datastore_submission_path + subm_id):
			comms.get_submission(config.datastore_submission_path + subm_id)
		path = self.compiled_bot_path(subm_id)
		if not os.path.exists(path):
			os.makedirs(path)
			target = (path )#+ "compile/")
#			os.makedirs (target)
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
	#		subprocess.call(["rm", "-rf", target])
			#print(subm.full_report())
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
		lang = ""
		if not (submission.language == None):
			lang = submission.language
		content = submission.vshort_message() + "\n" + lang + "\n" + submission.full_report()
		with open(path, 'w') as fo:
			fo.write(content)

	def send_compile_result(self, path, subm_id, game_id, submission):
		runfile = path + "run_command"
		if os.path.exists(runfile):	# make sure they don't put malicious commands in here, by deleting the file if it exists
			subprocess.call(["chmod", "u+rw", runfile])
			subprocess.call("rm", "-f", runfile)
		with open(runfile, 'w') as fo:
			fo.write(submission.get_command(config.worker_compiled + subm_id))
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
		filepath = path + "compiled" + config.delimiter + submission_id
		content = username + "\n" + game_id + "\n" + submission_id + "\n"
		with open (filepath, 'w') as fo:
			fo.write(content)
		comms.send_file_matchmaker_ready(filepath, config.matchmaker_path)

	def compiled_bot_path(self, bot):
		return config.worker_compiled + bot + "/"

	def get_compiled_bot(self, bot):
		path = self.compiled_bot_path(bot)
		os.mkdir(path)

		zipfile = bot + "-compiled.zip"
		comms.get_submission_from_filename(zipfile)
		subprocess.call(["unzip", "-j", "-o", config.datastore_submission_path + zipfile, "-d", path])

	def get_bot_command(self, bot):
		print(bot)
		path = self.compiled_bot_path(bot)
		if not os.path.exists(path):
			self.get_compiled_bot(bot)
		with open(path + "run_command") as fo:
			run_command = fo.readline().strip()
		print(run_command)
		return (path, run_command)

	def get_bot_commands(self, bots):
		print("Bot commands:")
		return [self.get_bot_command(bot) for bot in bots]

	def get_player_name(self, bot):
		return bot.split(config.delimiter)[0]

	def run_match(self, match):
		players = self.get_bot_commands(match.bots)
		player_names = [self.get_player_name(player) for player in match.bots]
		game_class = games.get_game(match.gamename)
		game = game_class(None, players, player_names, match.map_file)
		result = game.run_game()
		comms.send_result(match, result)

class Worker_data:
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

