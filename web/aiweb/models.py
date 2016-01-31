from django.db import models

# Create your models here.

class Submission(models.Model):
	username = models.CharField (max_length = 32)
	game_id = models.CharField (max_length = 32)
	timestamp = models.CharField (max_length = 32)
	submission_id = models.CharField (max_length = 100)
	language = models.CharField (max_length = 32, default="?")
	status = models.CharField (max_length = 32)
	report = models.CharField (max_length = 5000)
	

# This is for use by the matchmaking server with a separate DB
class Bot(models.Model):
	username = models.CharField (max_length = 32)
	game_id = models.CharField (max_length = 32)
	submission_id = models.CharField (max_length = 100)
	compile_time = models.DateTimeField(auto_now_add = True)
	games_played = models.DecimalField(decimal_places = 0, max_digits = 16)


