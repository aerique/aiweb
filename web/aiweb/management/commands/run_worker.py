from django.core.management.base import BaseCommand, CommandError

import aiweb_tools.worker.worker

class Command(BaseCommand):
	help = 'Runs a worker'

	def add_arguments(self, parser):
#		parser.add_argument('poll_id', nargs='+', type=int)
		pass

	def handle(self, *args, **options):
		worker = aiweb_tools.worker.worker.Worker()
		worker.request_task()
		self.stdout.write(self.style.SUCCESS('Running worker %s' % worker.uuid.hex))
		worker.await_task()

