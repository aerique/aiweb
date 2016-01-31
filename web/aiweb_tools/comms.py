import subprocess

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

def send_task_worker_ip(filepath, ip_addr):
	send_file_ready(filepath, config.task_username + "@" + ip_addr
			+ "://" + config.task_worker_path, config.task_port)

def send_stringfile (file_content, filename, target, send):
	f = open(filename, 'w')
	f.write(file_content)
	f.close()
	send(filename, target)
	

def filename(filepath):
	return filepath.split("/")[-1]

