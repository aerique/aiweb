import uuid
import datetime
import subprocess
import glob
import os.path
import time
import shutil

from .. import config

my_ip = "127.0.0.1" # Change this for each server running workers, unless using a single-server install for all parts including webserver
worker_temp = "/home/" + config.task_username + "aiweb/worker_tmp/"

class Worker:
	def __init__(self):
		self.uuid = uuid.uuid4()

	def task_request_content(self):
		content = my_ip + "\n" + self.uuid.hex
		return content

	def request_task(self):
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
				real = (file[:-len(ready))
				if (task_is_mine(real)):
					do_task(real)
					subprocess.call(["rm", real])
					subprocess.call(["rm", file])
			time.sleep(5)

		subprocess.call(["rm", stopfile])

		
	def task_is_mine(taskfile):
		with open(taskfile) as fo:
			line = fo.readline().trim()
			return line.endswith(self.uuid.hex)

	def do_task(taskfile):
		with open(taskfile) as fo:
			line = fo.readline().trim().split(" ")
			if len(line) < 2:
				print("Error: task file should have at least 2 columns")
				pass
			else:
				if line[0] == "compile":
					compile(line[1])

	def get_submission(filepath):
		subprocess.call(["scp", config.datastore_username + "@" + config.datatore_ip + "://" + filepath, filepath])

	def compile(submission):
		if not os.path.isfile(datastore_submission_path + submission):
			get_submission(datastore_submission_path + submission)
		path = worker_tmp + self.uuid.hex + "/"
		if not os.path.exists(path):
			os.makedirs(path)
		target = (path + "compile/")
		os.makedirs (target)
		shutil.copyfile (datastore_submission_path + submission, target)
		


