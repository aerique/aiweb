from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import forms
from django.template.context_processors import csrf
from django.shortcuts import render_to_response

import os
import logging

import aiweb.models

import aiweb_tools.comms
import aiweb_tools.manager.manager

#import imp

#manager = imp.load_source('manager', '../manager/manager.py')


# Create your views here.


def index(request):
	msg = "<p> <a href='/accounts/login'> Login </a> </p> <p> <a href='/accounts/register'> Register </a> </p>"
	return HttpResponse(msg)

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
	aiweb_tools.manager.manager.handle_submission(os.path.abspath(filepath), user.username) # ,gamename
#	aiweb_tools.manager.manager.assign_tasks()

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
		results = aiweb.models.Result.objects.all()
		results_count = results.count()
		results_limit = 25
		count_from = max(0, results_count - results_limit)
		results = reversed(results.order_by('id')[count_from:])
		c = {'form': form, 
			'user': request.user, 
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
			'replaydata': replaydata,
		}
		print(replaydata)
		if 'gamename' in replay:
			if replay['gamename'].lower() == "ants":
				return render_to_response('aiweb_templates/ants_visualizer.html', context)
			elif replay['gamename'].lower() == "tron":
				return render_to_response('aiweb_templates/tron_visualizer.html', context)
			else:
				return render_to_response('aiweb_templates/ants_visualizer.html', context)
		else:
			return render_to_response('aiweb_templates/ants_visualizer.html', context)


