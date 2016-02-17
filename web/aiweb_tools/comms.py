import subprocess
import cloudpickle
import os.path
import json
import datetime

from aiweb_tools import config

# FIXME Not checking for return codes after sending/getting files

def send_file(filepath, remote, port, dest):
	if "@127.0.0.1" in remote:
		if filepath.startswith(dest):
			print(filepath + " startswith " + dest)
		else:
			subprocess.call(["cp", filepath, dest])
	else:
		subprocess.call(["scp", "-P", str(port), remote + filepath, dest])

def get_file(remote, port, remotepath, targetpath):
	if "@127.0.0.1" in remote:
		if remotepath.startswith(targetpath):
			pass
		else:
			subprocess.call(["cp", remotepath, targetpath]);
	else:
		subprocess.call(["scp", "-P", port, remote + remotepath, targetpath]);

def send_file_ready(filepath, remote, port, dest):
	send_file(filepath, remote, port, dest)
	subprocess.call(["touch", filepath + ".ready"])
	send_file(filepath + ".ready", remote, port, dest)
	# FIXME on localhost, will this remove the file we just sent?
	subprocess.call(["rm", filepath + ".ready"])

def send_file_datastore_ready(filepath, target):
	remote = config.username + "@" + config.datastore_ip + "://"  
	port = config.datastore_port
	send_file_ready(filepath, remote, port, target)

def send_file_webserver_ready(filepath, target):
	remote = config.username + "@" + config.webserver_ip + "://"  
	port = config.webserver_port
	send_file_ready(filepath, remote, port, target)

def send_file_matchmaker_ready(filepath, target):
	remote = config.username + "@" + config.matchmaker_ip + "://"
	port = config.matchmaker_port
	send_file_ready(filepath, remote, port, target)

def send_file_taskserver_ready(filepath, target):
	remote = config.username + "@" + config.task_ip + "://"  
	port = config.task_port
	send_file_ready(filepath, remote, port, target)

def send_task_worker_ip(filepath, ip_addr):
	remote = config.username + "@" + ip_addr + "://"  
	port = config.task_port
	dest = config.task_worker_path
	send_file_ready(filepath, remote, port, dest)

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

def get_submission_from_filename(filename):
	remote = config.username + "@" + config.datastore_ip + "://"
	port = config.datastore_port
	remotepath = config.datastore_submission_path + filename
	targetpath = config.datastore_submission_path
	get_file(remote, port, remotepath, targetpath)
	
def get_submission(filepath):
	remote = config.username + "@" + config.datastore_ip + "://"
	get_file(remote, config.datastore_port, filepath, filepath)

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

def send_submission (filepath, destname):
	remote = config.username + "@" + config.datastore_ip + "://"
	port = config.datastore_port
	send_file(filepath, remote, port, destname)
	subprocess.call(["rm", filepath]);

def add_task(ip_addr, prefix, file_content):
	srcname = prefix + config.delimiter + (datetime.datetime.now().isoformat()).replace(":", "-")
	f = open(srcname, 'w')
	f.write(file_content)
	f.close()
	remote = config.username + "@" + ip_addr + "://"  
	port = config.task_port
	dest = config.task_path
	send_file(srcname, remote, port, dest)
	subprocess.call(["rm", srcname])



