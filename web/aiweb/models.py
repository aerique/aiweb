from django.db import models

# Create your models here.

class Submission(models.Model):
	username = models.CharField (max_length = 32)
	game_id = models.CharField (max_length = 32)
	timestamp = models.CharField (max_length = 32)
	submission_id = models.CharField (max_length = 100)
	status = models.CharField (max_length = 32)
	report = models.CharField (max_length = 5000)
	


