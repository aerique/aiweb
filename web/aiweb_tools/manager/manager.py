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
	srcname = prefix + "_" + (datetime.datetime.now().isoformat()).replace(":", "-")
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
	worker_fo = open(worker_file)
	worker_ip = worker_fo.readline().strip()
	worker_id = worker_fo.readline().strip()
	print(worker_ip)
	with open (task, "a") as taskfile:
		taskfile.write(" " + worker_id)
	print("id = " + worker_id)
	subprocess.call(["scp", task, config.task_username + "@" + worker_ip
			+ "://" + config.task_worker_path])
	subprocess.call(["touch", task + ".ready"])
	subprocess.call(["scp", task + ".ready", config.task_username + "@" + worker_ip
			+ "://" + config.task_worker_path])
	subprocess.call(["rm", task])
	subprocess.call(["rm", task + ".ready"])

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
		ending = ".ready"
		if (file.endswith(ending)):
			real = file[:-len(ending)]
			print(real)
			find_task(real)
			# FIXME needs to confirm task completion
			subprocess.call(["rm", file])
			subprocess.call(["rm", real])
	print('tasks assigned')

def process_report(path):
	real = path[:-len('.ready')]
	filename = real.split('/')[-1]
	prefix = filename.split('.')[0]
	parts = prefix.split('_')
	username = parts[0]
	game = parts[1]
	timestamp = parts[2]
	with open(real) as fo:
		content = fo.readlines()
		print(username)
		print(game)
		print(timestamp)
		print(content)


def process_reports():
	print("processing reports")
	for file in glob.glob(config.webserver_results_path + "*-report.txt.ready"):
		process_report(file)
