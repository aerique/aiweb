from django.core.management.base import BaseCommand, CommandError

import aiweb_tools.manager.manager
import aiweb.models

from aiweb_tools import config


import time
import os

class Command(BaseCommand):
	help = 'webserver backend'

	def add_arguments(self, parser):
		pass

	def handle(self, *args, **options):
		stopfile = (config.task_path + "stop_tasks")
		while not os.path.isfile(stopfile):

			# Assign tasks
			aiweb_tools.manager.manager.assign_tasks()
			self.stdout.write(self.style.SUCCESS('Assigning tasks'))

			# Process reports
			aiweb_tools.manager.manager.process_reports(aiweb_tools.manager.manager.add_submission_report)
			self.stdout.write(self.style.SUCCESS('Processed reports'))
			time.sleep(5)

		subprocess.call(["rm", stopfile])

