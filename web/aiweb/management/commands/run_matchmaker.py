from django.core.management.base import BaseCommand, CommandError

import aiweb_tools.matchmaker

class Command(BaseCommand):
	help = 'Runs a worker'

	def add_arguments(self, parser):
#		parser.add_argument('poll_id', nargs='+', type=int)
		pass

	def handle(self, *args, **options):
		matchmaker = aiweb_tools.matchmaker.Matchmaker()
		self.stdout.write(self.style.SUCCESS('Running matchmaker'))
		matchmaker.await_request()

