import uuid
import imp

from .. import config

class Worker:
	def __init__(self):
		self.uuid = uuid.uuid4()

	def request_task(self):
		srcname = "worker-ready_" + (datetime.datetime.now().isoformat()).replace(":", "-") + self.uuid
		f = open(srcname, 'w')
		f.write(file_content)
		f.close()
		subprocess.call(["scp", srcname, config.task_username + "@" + 
			ip_addr + "://" +
			config.task_worker_path ]);
		ready_filename = srcname + ".ready"

		subprocess.call(["touch", ready_filename])
		subprocess.call(["scp", ready_filename, config.task_username + "@" + 
			ip_addr + "://" +
			config.task_worker_path ]);
		subprocess.call(["rm", srcname])
		subprocess.call(["rm", ready_filename])
		

	def await_task(self):
		pass
