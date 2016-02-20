from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import forms
from django.template.context_processors import csrf
from django.shortcuts import render_to_response

import glob

import os
import logging
import textwrap

import aiweb.models

import aiweb_tools.comms
import aiweb_tools.manager
from aiweb_tools import config

#import imp

#manager = imp.load_source('manager', '../manager/manager.py')


# Create your views here.


def index(request):
	results = get_results(request, None, None, config.results_limit)
	c = {'results_list' : results,
		'user': request.user, 
		'games': config.games_active,
	}
	return render_to_response('aiweb_templates/index.html', c)
#	msg = "<p> <a href='/accounts/login'> Login </a> </p> <p> <a href='/accounts/register'> Register </a> </p>"
#	return HttpResponse(msg)

class UploadFileForm(forms.Form):
	file  = forms.FileField()

def handle_uploaded_file(ffile, user):
	path = ("uploads/" + user.username)
	if not os.path.exists(path):
		os.makedirs(path)

	filepath = (path + "/" + ffile.name)
	with open(filepath, 'wb+') as destination:
		for chunk in ffile.chunks():
			destination.write(chunk)
			destination.close()
	aiweb_tools.manager.handle_submission(os.path.abspath(filepath), user.username) # ,gamename
#	aiweb_tools.manager.manager.assign_tasks()

def get_result_error(request, result):
	retval = ""
	for count, error in enumerate(result.bot_errors.all()):
		if result.player_name(count) == request.user.username:
			retval += str(error.text)
	return retval

def add_error_messages(request, results):
	""" Add error messages for request.user to results """
	retval = []
	if (request.user.is_authenticated()):
		for result in results:
			retval.append ({'error' : get_result_error(request, result),
				'result' : result
			})
			#result.error_message = get_result_error(request, result)
	else:
		for result in results:
			retval.append ({'error' : "",
				'result' : result
			})
	return retval

def add_playerlines(request, results):
	for presult in results:
		result = presult['result']
		zipped = zip(result.ranks_plus_one_as_list(), result.player_names_as_list(), result.statuses_as_list())
		playerlines = []
		sortzip = sorted(zipped, key=lambda r: (r[0]))
		for rank, player, status in sortzip:
			playerlines.append("&nbsp;[" + str(rank) + "]&nbsp;  " + player + "&nbsp;  (" + status + ")&nbsp;")
		presult['playerlines'] = playerlines
	

def match_results(request, gamename):
	results = get_results(request, None, gamename, config.results_limit)
	c = {
		'user':request.user,
		'gamename':gamename,
		'results_list':results,
		'games': config.games_active,
	}
	return render_to_response('aiweb_templates/results_page.html', c)


def get_results(request, username, gamename, limit):
	presults = aiweb.models.Result.objects
	if gamename:
		print(gamename)
		presults = presults.filter(gamename__startswith=gamename, gamename__endswith=gamename)
	if username:
		presults = presults.filter(player_names__contains=username)
	results = presults.all()
	results_count = results.count()
	results_limit = limit
	count_from = max(0, results_count - results_limit)
	results = results.order_by('id')[count_from:]
	with_errors = add_error_messages(request, results)
	add_playerlines(request, with_errors)
#	logging.log(logging.ERROR, str(with_playerlines[0]))
	results = reversed(with_errors)
	return results

def profile(request, status="normal"):
	if request.method == 'POST':
		a=request.POST
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			#print(dir(form))
			if not (request.FILES['file']) == "":
				handle_uploaded_file(request.FILES['file'], request.user)
				return HttpResponseRedirect('/aiweb/profile/upload_success/')
			else:
				return HttpResponseRedirect('/aiweb/profile/')
		else: 
			return HttpResponseRedirect('/aiweb/profile/')
	else:
		form = UploadFileForm()
		upload_success = (status == "upload_success")
		submissions = aiweb.models.Submission.objects.filter(username=request.user.username)
		subm_count = submissions.count()
		subm_limit = 5
		count_from = max(0, subm_count - subm_limit)
		submissions = reversed(submissions.order_by('timestamp')[count_from:])
#		results = aiweb.models.Result.objects.all()
#		results_count = results.count()
#		results_limit = 25
#		count_from = max(0, results_count - results_limit)
#		results = reversed(results.order_by('id')[count_from:])
		results = get_results(request, request.user.username, None, config.results_limit)
		c = {'form': form, 
			'user': request.user, 
			'games': config.games_active,
			'upload_success': upload_success,
			'submissions': submissions,
			'results_list': results}
#		for result in results:
#			for error in result.bot_errors.all():
#				print(error.text)
		c.update(csrf(request))
		return render_to_response('aiweb_templates/profile.html', c)

def replay(request, id="none"):
	if not (id=="none"):
		replaydata = aiweb_tools.comms.load_replaydata(id)
		replay = aiweb_tools.comms.load_replay(id)
		context = {
			'user' : request.user,
			'replaydata': replaydata,
			'games': config.games_active,
		}
		print(replaydata)
		# refactor :)
		if 'gamename' in replay:
			if replay['gamename'].lower() == "ants":
				return render_to_response('aiweb_templates/ants_visualizer.html', context)
			elif replay['gamename'].lower() == "tron":
				return render_to_response('aiweb_templates/tron_visualizer.html', context)
			else:
				return render_to_response('aiweb_templates/ants_visualizer.html', context)
		else:
			return render_to_response('aiweb_templates/ants_visualizer.html', context)


def rank(request, gamename=config.games_active[0]):
	context={'user' : request.user,
		'gamename':gamename,
		'games': config.games_active,
	}
	q1 = aiweb.models.Submission.objects.filter(game_id=gamename).filter(active=True).order_by('skill')
	limit = q1.count()
	ranks = q1[max(0, limit - 100):].all().reverse()
	context['ranks'] = ranks
	return render_to_response('aiweb_templates/rank.html', context)

def report(request, id="0000"):
	try:
		subm = aiweb.models.Submission.objects.filter(submission_id=id).get()
		report = subm.report
		if report == "":
			report = "Nothing to report"
		else:
			acc = []
			for line in report.split('\n'):
				acc = acc + textwrap.wrap(line, width=78)
				acc = acc + ["\n"]
			report = acc
		context={'user': request.user,
			'submission' : subm,
			'report' : report,
		}
		return render_to_response('aiweb_templates/report.html', context)
	except Exception:
		report = ["Error: That submission does not exist"]
		context={'user': request.user,
			'submission' : {'username':request.user.username},
			'report' : report,
		}
		return render_to_response('aiweb_templates/report.html', context)

def game_info(request, gamename=config.games_active[0]):
		context = {'user': request.user, 
			'games': config.games_active,
			'gamename' : gamename,
			}
		return render_to_response('aiweb_templates/' + gamename + '_info.html', context)

def problem_description(request, gamename=config.games_active[0]):
		context = {'user': request.user, 
			'games': config.games_active,
			'gamename' : gamename,
			}
		return render_to_response('aiweb_templates/' + gamename + '_problem.html', context)

def starter_packages(request, gamename=config.games_active[0]):
		dist = ('/static/aiweb/' + gamename.lower() + '/' + gamename + '_dist.zip', gamename + '_dist.zip')
		starters = []
		starterpath = gamename.lower() + "/starter/" + gamename + "*.zip"
		for filepath in glob.glob(config.webserver_staticfiles + starterpath):
			filename = filepath.split('/')[-1]
			starters.append((filepath.replace(config.webserver_staticfiles, "/static/aiweb/"), filename))
		context = {'user': request.user, 
			'games': config.games_active,
			'gamename' : gamename,
			'dist': dist,
			'starters': starters,
			}
		return render_to_response('aiweb_templates/starter.html', context)

def mission(request):
		context = {'user': request.user, 
			'games': config.games_active,
			}
		return render_to_response('aiweb_templates/mission.html', context)

def contact(request):
		context = {'user': request.user, 
			'games': config.games_active,
			}
		return render_to_response('aiweb_templates/contact.html', context)


