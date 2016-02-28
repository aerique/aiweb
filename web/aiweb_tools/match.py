#   Copyright 2016 The aichallenge Community
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import uuid
import cloudpickle

class Match:

	for_worker = ""
	gamename = "NoGame"
	map_file = ""
	bots = []

	def __init__(self):
		self.uuid = uuid.uuid4()
		self.bots = []

	def add_bot(self, bot):
		self.bots.append(bot)

	def set_for_worker(self, for_worker):
		self.for_worker = for_worker

	def write_file(self, filepath):
		with open(filepath, 'wb') as fo:
			cloudpickle.dump(self, fo)
	
	def read(self, filepath):
		with open(filepath, 'rb') as fo:
			match = cloudpickle.load(fo)
			self.for_worker = match.for_worker
			self.gamename = match.gamename
			self.map_file = match.map_file
			self.uuid = match.uuid
			self.bots = match.bots


	def short_string(self):
		return self.gamename + self.uuid.hex

