from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django import forms
from django.template.context_processors import csrf
from django.shortcuts import render_to_response

import os

import logging

#import imp

#manager = imp.load_source('manager', '../manager/manager.py')

import aiweb_tools.manager.manager

# Create your views here.


def index(request):
    msg = "<p> <a href='/accounts/login'> Login </a> </p> <p> <a href='/accounts/register'> Register </a> </p>"
    return HttpResponse(msg)

#def profile(request):
#    if request.user.is_authenticated():
#        msg = "<p> You are logged in, " + request.user.get_username() +  ". </p>"
#    else:
#        msg = "<p> You are not logged in. </p>"
#    return HttpResponse(msg)



#def profile(request):
#    template = loader.get_template('aiweb_templates/profile.html')
#    context = {}
#    return HttpResponse(template.render(context, request))

class UploadFileForm(forms.Form):
    file  = forms.FileField()

def handle_uploaded_file(ffile, user, gamename):
    path = ("uploads/" + user.username)
    if not os.path.exists(path):
        os.makedirs(path)

    filepath = (path + "/" + ffile.name)
    with open(filepath, 'wb+') as destination:
        for chunk in ffile.chunks():
            destination.write(chunk)
            destination.close()
    aiweb_tools.manager.manager.handle_submission(os.path.abspath(filepath), user.username, gamename)
    aiweb_tools.manager.manager.assign_tasks()

def profile(request, status="normal"):
    if request.method == 'POST':
        a=request.POST
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #print(dir(form))
            handle_uploaded_file(request.FILES['file'], request.user, form.data['gamename'])
            return HttpResponseRedirect('/aiweb/profile/upload_' + form.data['gamename']+ '_success/')
    else:
        form = UploadFileForm()
        upload_tron_success = (status == "upload_Tron_success")
        upload_ants_success = (status == "upload_Ants_success")
        c = {'form': form, 
             'user': request.user, 
             'upload_tron_success': upload_tron_success,
             'upload_ants_success': upload_ants_success,
	     }
        c.update(csrf(request))
        return render_to_response('aiweb_templates/profile.html', c)
