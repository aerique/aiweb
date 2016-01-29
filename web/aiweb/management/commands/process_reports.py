from django.core.management.base import BaseCommand, CommandError

import aiweb_tools.manager.manager

import aiweb.models

class Command(BaseCommand):
	help = 'process reports'

	def add_arguments(self, parser):
#		parser.add_argument('poll_id', nargs='+', type=int)
		pass

	def add_submission_report(self, username, game, timestamp, prefix, status, language, content):
		subm = aiweb.models.Submission.objects.create(
			username = username,
			game_id = game,
			timestamp = timestamp,
			submission_id = prefix,
			status = status,
			language = language,
			report = content)
		subm.save()
		
	def handle(self, *args, **options):
		aiweb_tools.manager.manager.process_reports(self.add_submission_report)
		self.stdout.write(self.style.SUCCESS('Processed reports'))



