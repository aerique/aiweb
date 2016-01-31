import aiweb_tools.comms

class Matchmaker:
	def await_request(self):
		stopfile = (config.matchmaker_path + "stop_matchmaker") 
		while not os.path.isfile(stopfile):
			ready = ".ready"
			for file in glob.glob(config.matchmaker_path + "*" + ready):
				print(file)
				real = (file[:-len(ready)])
				self.process_request(real)
				subprocess.call(["rm", real])
				subprocess.call(["rm", file])
			time.sleep(5)
			print("checking for requests")

		subprocess.call(["rm", stopfile])

	def process_request(self, filepath):
		filename = aiweb_tools.comms.filename(filename)
		if filename.startswith('compiled'):
			self.add_compile_data(filepath)
		else:
			self.make_match_for_worker(filepath)

	def add_compile_data(self, filepath):
		with fo as open(filepath):
			username = fo.readline()
			game_id = fo.readline()
			submission_id = fo.readline()
			# add to matchmaker db

	def  make_match_for_worker(self, filepath):
		pass
