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
		srcname = "worker-ready_" + (datetime.datetime.now().isoformat()).replace(":", "-") + "_" + self.uuid.hex
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
		stopfile = (config.task_worker_path + "stop_" + self.uuid.hex) 
		while not os.path.isfile(stopfile):
			ready = ".ready"
			for file in glob.glob(config.task_worker_path + "*" + ready):
				print(file)
				real = (file[:-len(ready)])
				if (self.task_is_mine(real)):
					self.do_task(real)
					subprocess.call(["rm", real])
					subprocess.call(["rm", file])
			time.sleep(5)
			print("checking for tasks")

		subprocess.call(["rm", stopfile])

		
	def task_is_mine(self, taskfile):
		fname = taskfile.split("/")[-1]
		if fname.startswith("compile"):
			with open(taskfile) as fo:
				line = fo.readline().strip()
				return line.endswith(self.uuid.hex)
		elif fname.startswith("match_"):
			stripped = fname.strip("match_")
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
		self.request_task()

	def get_submission(self, filepath):
		subprocess.call(["scp", config.datastore_username + "@" + config.datatore_ip + "://" + filepath, filepath])

	def compile(self, submission):
		print("compiling: " + submission)
		if not os.path.isfile(config.datastore_submission_path + submission):
			get_submission(config.datastore_submission_path + submission)
		path = config.worker_compiled + submission + "/"
		if not os.path.exists(path):
			os.makedirs(path)
			target = (path )#+ "compile/")
#			os.makedirs (target)
			subprocess.call(["unzip", config.datastore_submission_path + submission, "-d", target])
	
			subm_data = submission.split("_")
			username = subm_data[0]
			game_id = subm_data[1]
			print("username" + username)
			subm = aiweb_tools.zeta.submission.Submission(username, submission, target)
			subm.compile()
	#		subprocess.call(["rm", "-rf", target])
			#print(subm.full_report())
			self.send_compile_result(path, submission, game_id, subm)

	def save_report(self, submission, path):
		lang = ""
		if not (submission.language == None):
			lang = submission.language
		content = submission.vshort_message() + "\n" + lang + "\n" + submission.full_report()
		with open(path, 'w') as fo:
			fo.write(content)

	def send_compile_result(self, path, sub_id, game_id, submission):
		zipfile = path + sub_id + "-compiled.zip"
		#subprocess.call(["ls", path])
		subprocess.call(["zip", "-r", zipfile, path, "-i", path + "*"])
		comms.send_file_datastore_ready(zipfile, config.datastore_submission_path)
		reportfile = path + sub_id + "-report.txt" 
		self.save_report(submission, reportfile)
		comms.send_file_webserver_ready(reportfile, config.webserver_results_path)
		self.send_matchmaker_compile_info(path, submission.username, game_id, sub_id)

	def send_matchmaker_compile_info(self, path, username, game_id, submission_id):
		filepath = path + "compiled_" + submission_id
		content = username + "\n" + game_id + "\n" + submission_id + "\n"
		with open (filepath, 'w') as fo:
			fo.write(content)
		comms.send_file_matchmaker_ready(filepath, config.matchmaker_path)
		

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

