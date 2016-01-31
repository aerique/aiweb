class Matchmaker:
	def await_request(self):
		stopfile = (config.matchmaker_path + "stop_matchmaker") 
		while not os.path.isfile(stopfile):
			ready = ".ready"
			for file in glob.glob(config.matchmaker_path + "*" + ready):
				print(file)
				real = (file[:-len(ready)])
				self.make_match_for_worker(real)
				subprocess.call(["rm", real])
				subprocess.call(["rm", file])
			time.sleep(5)
			print("checking for requests")

		subprocess.call(["rm", stopfile])

	def  make_match_for_worker(self):
		pass
