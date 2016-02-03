import uuid

class Match:

	for_worker = ""
	gamename = "NoGame"
	bots = []

	def __init__(self):
		self.uuid = uuid.uuid4()

	def add_bot(self, bot):
		self.bots.append(bot)

	def set_for_worker(self, for_worker):
		self.for_worker = for_worker

	def write_file(self, filepath):
		with open(filepath, 'w') as fo:
			fo.write(self.gamename + "\n")
			fo.write(self.for_worker + "\n")
			fo.write(str(len(self.bots)) + "\n")
			for bot in self.bots:
				fo.write(bot + "\n")
	
	def read(self, filepath):
		with open(filepath) as fo:
			self.gamename = fo.readline().strip()
			print("gamename = " + self.gamename)
			self.for_worker = fo.readline().strip()
			print("for_worker = " + self.for_worker)
			num_bots = int(fo.readline().strip())
			for i in range(0, num_bots):
				self.add_bot(fo.readline().strip())

	def short_string(self):
		return self.gamename + self.uuid.hex

