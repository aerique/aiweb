import subprocess
import cloudpickle
import os.path
import json

from aiweb_tools import config

def send_file(filepath, dest, port):
	subprocess.call(["scp", "-P", str(port), filepath, dest])

def send_file_ready(filepath, dest, port):
	send_file(filepath, dest, port)
	subprocess.call(["touch", filepath + ".ready"])
	send_file(filepath + ".ready", dest, port)
	subprocess.call(["rm", filepath + ".ready"])

def send_file_datastore_ready(filepath, target):
	send_file_ready(filepath, config.datastore_username + "@" 
			+ config.datastore_ip
			+ "://" + target, config.datastore_port)

def send_file_webserver_ready(filepath, target):
	send_file_ready(filepath, config.webserver_username + "@" 
			+ config.webserver_ip
			+ "://" + target, config.webserver_port)

def send_file_matchmaker_ready(filepath, target):
	send_file_ready(filepath, config.matchmaker_username + "@" 
			+ config.matchmaker_ip
			+ "://" + target, config.matchmaker_port)

def send_file_taskserver_ready(filepath, target):
	send_file_ready(filepath, config.task_username + "@" 
			+ config.task_ip
			+ "://" + target, config.task_port)

def send_task_worker_ip(filepath, ip_addr):
	send_file_ready(filepath, config.task_username + "@" + ip_addr
			+ "://" + config.task_worker_path, config.task_port)

def send_stringfile (file_content, filename, target, send):
	f = open(filename, 'w')
	f.write(file_content)
	f.close()
	send(filename, target)

def send_result (match, result):
	filename = match.uuid.hex + "-match-result.txt"
	f = open(filename, 'wb')
	cloudpickle.dump(result, f)
	f.close()
	send_file_webserver_ready(filename, config.webserver_results_path)
	subprocess.call(["rm", filename])

def have_submission(filename):
	return os.path.exists(config.datastore_submission_path)

def get_submission(filename):
	subprocess.call(["scp", config.datastore_username + 
		"@" + config.datastore_ip + "://" + 
		config.datastore_submission_path + filename, 
		config.datastore_submission_path])
	

def load_replaydata(id):
	path = config.webserver_results_path + id
	with open(path, 'r') as fo:
		replay = fo.readline()
	return replay

def load_replay(id):
	path = config.webserver_results_path + id
	with open(path, 'r') as fo:
		replay = json.load(fo)
	return replay


def filename(filepath):
	return filepath.split("/")[-1]

def get_replay_id():
	filepath = config.webserver_results_path + "replay_id.txt"
	if not os.path.exists(filepath):
		with open(filepath, 'w') as fo:
			fo.write(str(0))
	with open(filepath) as fo:
		this_id = int(fo.readline().strip())
	next_id = this_id + 1
	with open(filepath, 'w') as fo:
		fo.write(str(next_id))
	return this_id


