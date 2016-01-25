import uuid
import imp


class Worker:
	def __init__(self):
		self.uuid = uuid.uuid4()

	def request_task(self):
		pass
