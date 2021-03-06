username = "aiweb"
games_defunct = []
games_active = ["Tron", "Ants", "PlanetWars"]

prefix = "/home/" + username + "/aiweb/"

task_ip = "127.0.0.1"
task_port = 22
task_path = prefix + "tasks/"
task_worker_path = prefix + "worker/"

datastore_ip = "127.0.0.1"
datastore_port = 22
datastore_username = username
datastore_submission_path = prefix + "submissions/"

webserver_ip = "127.0.0.1"
webserver_port = 22
webserver_results_path = prefix + "results/"
webserver_staticfiles = "/home/" + username + "/ast/source/aiweb/web/aiweb/static/aiweb/"
 
matchmaker_ip = "127.0.0.1"
matchmaker_port = 22
matchmaker_path = prefix + "matchmaker/"

map_path = prefix + "maps/" # maps stored on matchmaker server

isolate_bin = prefix + "web/aiweb_tools/isolate/isolate"
worker_compiled = prefix + "compiled/"
runner_working = prefix + "runner/"
runner_prefix = "aiweb"
lock_dir = prefix + "lock/"
bin_dir = "/usr/bin/"
temp_dir = prefix + "temp/"

sleeptime = 0.5
delimiter = "____" # FIXME filter for this in usernames!

results_limit = 25
profile_results_limit = 5



