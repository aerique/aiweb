import uuid
import datetime
import subprocess
import glob

from .. import config

my_ip = "127.0.0.1" # Change this for each server running workers, unless using a single-server install for all parts including webserver

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
		subprocess.call(["scp", ready_filename, config.task_username + "@" + 
			config.task_ip + "://" +
			config.task_worker_path ]);
		subprocess.call(["rm", srcname])
		subprocess.call(["rm", ready_filename])
		

	def await_task(self):
		pass
