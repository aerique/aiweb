from django.core.management.base import BaseCommand, CommandError

import aiweb_tools.manager.manager

from aiweb_tools import config

import time

class Command(BaseCommand):
	help = 'webserver backend'

	def add_arguments(self, parser):
		pass

	def handle(self, *args, **options):
		stopfile = (config.task_path + "stop_tasks")
		while not os.path.isfile(stopfile):
			aiweb_tools.manager.manager.assign_tasks()
			self.stdout.write(self.style.SUCCESS('Assigning tasks'))
			aiweb_tools.manager.manager.process_reports(self.add_submission_report)
			self.stdout.write(self.style.SUCCESS('Processed reports'))
			time.sleep(5)
		subprocess.call(["rm", stopfile])

