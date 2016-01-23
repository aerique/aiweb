from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django import forms
from django.template.context_processors import csrf
from django.shortcuts import render_to_response

import os
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

def handle_uploaded_file(ffile, user):
    path = ("uploads/" + user.username)
    if not os.path.exists(path):
        os.makedirs(path)

    with open(path + "/" + ffile.name, 'wb+') as destination:
        for chunk in ffile.chunks():
            destination.write(chunk)

def profile(request, status="normal"):
    if request.method == 'POST':
        a=request.POST
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.user)
            return HttpResponseRedirect('/aiweb/profile/upload_success/')
    else:
        form = UploadFileForm()
        upload_success = (status == "upload_success")
        c = {'form': form, 
             'user': request.user, 
             'upload_success': upload_success}
        c.update(csrf(request))
        return render_to_response('aiweb_templates/profile.html', c)
