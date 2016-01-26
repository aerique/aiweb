from django.core.management.base import BaseCommand, CommandError

import aiweb_tools.manager.manager

class Command(BaseCommand):
	help = 'assign tasks'

	def add_arguments(self, parser):
#		parser.add_argument('poll_id', nargs='+', type=int)
		pass

	def handle(self, *args, **options):
		aiweb_tools.manager.manager.assign_tasks()
		self.stdout.write(self.style.SUCCESS('Assigning tasks'))


