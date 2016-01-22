from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

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



def profile(request):
    template = loader.get_template('aiweb_templates/profile.html')
    context = {}
    return HttpResponse(template.render(context, request))

