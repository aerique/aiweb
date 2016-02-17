from django.core.management.base import BaseCommand, CommandError

import aiweb_tools.manager

import aiweb.models

#WARNING this command is redundant and should be removed. FIXME

class Command(BaseCommand):
	help = 'process reports'

	def add_arguments(self, parser):
#		parser.add_argument('poll_id', nargs='+', type=int)
		pass
#WARNING duplicate of code in website_backend command
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
		aiweb_tools.manager.process_reports(self.add_submission_report)
		self.stdout.write(self.style.SUCCESS('Processed reports'))



