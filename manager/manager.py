import logging
import subprocess

manager_ip = "127.0.0.1"
manager_port = 22
datastore_ip = "127.0.0.1"
datastore_port = 22
datastore_username = "smiley"
datastore_submission_path = "/home/" + datastore_username + "/submissions/"

def send_submission (filepath):

    # FIXME No checking for return codes

    subprocess.call(["sync"])
    print(" ".join(["scp", filepath, datastore_username + "@" + 
                  datastore_ip + "://" +
                  datastore_submission_path]))
    subprocess.call(["scp", filepath, datastore_username + "@" + 
                    datastore_ip + "://" +
                    datastore_submission_path]);

    ready_filename = filepath + ".ready"

    subprocess.call(["touch", ready_filename]);

    subprocess.call(["scp", ready_filename, datastore_username + "@" + 
                    datastore_ip + "://" + 
		    datastore_submission_path]);

    subprocess.call(["rm", ready_filename]);

    subprocess.call(["rm", filepath]);


def handle_submission(filepath, username):

    # FIXME 
    logging.info("Processing submission at " + filepath);

    send_submission (filepath)
