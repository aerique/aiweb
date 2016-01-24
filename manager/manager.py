import logging
import subprocess
import datetime

# FIXME before publication, change username!

task_ip = "127.0.0.1"
task_port = 22
task_username = "smiley"
task_path = "/home/" + task_username + "/aiweb/tasks/"

datastore_ip = "127.0.0.1"
datastore_port = 22
datastore_username = "smiley"
datastore_submission_path = "/home/" + datastore_username + "/aiweb/submissions/"

#temp_dir = "temp/"

def send_submission (filepath, destname):

    # FIXME No checking for return codes
    # FIXME not using port


    subprocess.call(["sync"])
    subprocess.call(["scp", filepath, datastore_username + "@" + 
                    datastore_ip + "://" +
                    datastore_submission_path + destname]);

    ready_filename = filepath + ".ready"

    subprocess.call(["touch", ready_filename]);

    subprocess.call(["scp", ready_filename, datastore_username + "@" + 
                    datastore_ip + "://" + 
		    datastore_submission_path + destname+ ".ready"]);

    subprocess.call(["rm", ready_filename]);

    subprocess.call(["rm", filepath]);

def add_task(prefix, file_content):
    srcname = prefix + (datetime.datetime.now().isoformat()).replace(":", "-")
    f = open(srcname, 'w')
    f.write(file_content)
    f.close()
    subprocess.call(["scp", srcname, task_username + "@" + 
                    task_ip + "://" +
                    task_path ]);
    subprocess.call(["rm", srcname])

def handle_submission(filepath, username, gamename):

    logging.info("Processing submission at " + filepath);

    destname = username + "_" + gamename + "_" + (datetime.datetime.now().isoformat()).replace(":", "-")

    send_submission (filepath, destname)

    # FIXME better protection against filename collisions desirable
    add_task ("compile", "compile " + destname)
