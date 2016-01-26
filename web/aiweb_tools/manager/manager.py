import logging
import subprocess
import datetime
import glob

import sys
from django.core.management.base import BaseCommand

from .. import config

def send_submission (filepath, destname):

	# FIXME No checking for return codes
	# FIXME not using port


	subprocess.call(["sync"])
	subprocess.call(["scp", filepath, config.datastore_username + "@" + 
					config.datastore_ip + "://" +
					config.datastore_submission_path + destname]);

# Probably not needed - submission will never be looked at until compile 
# task has been added to task list.

#	ready_filename = filepath + ".ready"

#	subprocess.call(["touch", ready_filename]);

#	subprocess.call(["scp", ready_filename, datastore_username + "@" + 
#					datastore_ip + "://" + 
#			datastore_submission_path + destname+ ".ready"]);

#	subprocess.call(["rm", ready_filename]);

	subprocess.call(["rm", filepath]);

def add_task(ip_addr, prefix, file_content):
	srcname = prefix + (datetime.datetime.now().isoformat()).replace(":", "-")
	f = open(srcname, 'w')
	f.write(file_content)
	f.close()
	subprocess.call(["scp", srcname, config.task_username + "@" + 
					ip_addr + "://" +
					config.task_path ]);
	subprocess.call(["rm", srcname])

def handle_submission(filepath, username, gamename):

	print("Processing submission at " + filepath);

	destname = username + "_" + gamename + "_" + (datetime.datetime.now().isoformat()).replace(":", "-")

	send_submission (filepath, destname)

	# FIXME better protection against filename collisions desirable
	add_task (config.task_ip, "compile", "compile " + destname)

def send_task_to_worker(task, worker_file):
	print("send_task_to_worker")
#	worker_fo = open(worker_file)
#	worker_ip = worker_fo.readline()
	worker_ip = open(worker_file).readline().strip()
	print("worker_ip = " + worker_ip)

#	worker_ip = worker_ip[:-1]
#	print("worker_ip = " + worker_ip)
#	worker_ip = worker_ip.strip()
#	print("worker_ip = " + worker_ip) # Something weird was going on here
	print (" ".join(["scp", task, config.task_username + "@" + worker_ip + "://" + config.task_worker_path]))
	subprocess.call(["scp", task, config.task_username + "@" + worker_ip
			+ "://" + config.task_worker_path])
	subprocess.call(["rm", task])

def process_game(blah):
	pass

def find_task(worker_file):
	tasks = glob.glob(config.task_path + "*")
	finished = 0
	for task in tasks:
		if (finished == 0):
			taskname = task.split("/")[-1]
			if not (taskname.startswith("worker-ready")):
				send_task_to_worker (task, worker_file)
				finished = 1
	if (finished == 0):
		process_game(worker_file)

def assign_tasks():
	print('Assigning tasks')
#	tasks = glob.glob(task_path + "*")
#	for task in tasks:
#		print("Task: " + task.split("/")[-1])
	for file in glob.glob(config.task_worker_path + "worker-ready*"):
		print ("considering task file: " + file)
		if (file.endswith(".ready")):
			pass
		else:
			print(file)
			find_task(file)
			subprocess.call(["rm", file])
			subprocess.call(["rm", file + ".ready"])
	print('tasks assigned')

