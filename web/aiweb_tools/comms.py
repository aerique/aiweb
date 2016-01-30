import subprocess

from aiweb_tools import config

def send_file(filepath, dest):
	subprocess.call(["scp", filepath, dest])

def send_file_ready(filepath, dest):
	send_file(filepath, dest)
	subprocess.call(["touch", filepath + ".ready"])
	send_file(filepath + ".ready", dest)
	subprocess.call(["rm", filepath + ".ready"])

def send_file_datastore_ready(filepath, target):
	send_file_ready(filepath, config.datastore_username + "@" 
			+ config.datastore_ip
			+ "://" + target)

def send_file_webserver_ready(filepath, target):
	send_file_ready(filepath, config.webserver_username + "@" 
			+ config.webserver_ip
			+ "://" + target)

