import subprocess

from aiweb_tools import config

def send_file_datastore_ready(filepath, target):
	subprocess.call(["scp", filepath, config.datastore_username + "@" 
			+ config.datastore_ip
			+ "://" + target])
	subprocess.call(["touch", filepath + ".ready"])
	subprocess.call(["scp", filepath + ".ready", 
			config.datastore_username + "@" + config.datastore_ip
			+ "://" + target])
	subprocess.call(["rm", filepath + ".ready"])

#FIXME refactor
def send_file_webserver_ready(filepath, target):
	subprocess.call(["scp", filepath, config.webserver_username + "@" 
			+ config.webserver_ip
			+ "://" + target])
	subprocess.call(["touch", filepath + ".ready"])
	subprocess.call(["scp", filepath + ".ready", 
			config.webserver_username + "@" + config.webserver_ip
			+ "://" + target])
	subprocess.call(["rm", filepath + ".ready"])

