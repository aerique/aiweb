import uuid
import datetime
import subprocess
import glob
import os.path
import time
import shutil

from .. import config
import aiweb_tools.zeta.submission

my_ip = "127.0.0.1" # Change this for each server running workers, unless using a single-server install for all parts including webserver
worker_temp = "/home/" + config.task_username + "/aiweb/worker_tmp/"

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
		with open(taskfile) as fo:
			line = fo.readline().strip()
			return line.endswith(self.uuid.hex)

	def do_task(self, taskfile):
		print("doing task: " + taskfile)
		with open(taskfile) as fo:
			line = fo.readline().strip().split(" ")
			if len(line) < 2:
				print("Error: task file should have at least 2 columns")
				pass
			else:
				if line[0] == "compile":
					self.compile(line[1])
		self.request_task()

	def get_submission(self, filepath):
		subprocess.call(["scp", config.datastore_username + "@" + config.datatore_ip + "://" + filepath, filepath])

	def compile(self, submission):
		print("compiling: " + submission)
		if not os.path.isfile(config.datastore_submission_path + submission):
			get_submission(config.datastore_submission_path + submission)
		path = worker_temp + self.uuid.hex + "/"
		if not os.path.exists(path):
			os.makedirs(path)
		target = (path + "compile/")
		os.makedirs (target)
		shutil.copyfile (config.datastore_submission_path + submission, target + submission)

		subm_data = "_".split(submission)
		username = subm_data[0]
		print(username)
		subm = aiweb_tools.zeta.submission.Submission(username, submission, path)
		


