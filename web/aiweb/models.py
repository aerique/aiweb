from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Submission(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	username = models.CharField (max_length = 32)
	game_id = models.CharField (max_length = 32)
	timestamp = models.CharField (max_length = 32)
	submission_id = models.CharField (max_length = 100)
	language = models.CharField (max_length = 32, default="?")
	status = models.CharField (max_length = 32)
	report = models.CharField (max_length = 5000)
	
class Result(models.Model):
	submissions = models.ManyToManyField(Submission)
	player_names = models.CharField (max_length = 650)
	scores = models.CharField (max_length = 100)
	statuses = models.CharField (max_length = 100)
	ranks = models.CharField (max_length = 100)
	game_message = models.CharField (max_length = 100)
	replay = models.CharField (max_length = 100)


# This is for use by the matchmaking server with a separate DB
class Bot(models.Model):
	username = models.CharField (max_length = 32)
	game_id = models.CharField (max_length = 32)
	submission_id = models.CharField (max_length = 100)
	compile_time = models.DateTimeField(auto_now_add = True)
	games_played = models.DecimalField(decimal_places = 0, max_digits = 16)
	rank = models.DecimalField(decimal_places = 0, max_digits = 16, default = 0)
	selection_weight = models.DecimalField(decimal_places = 12, max_digits = 24, default = 1)

