from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def index(request):
    template = loader.get_template('website/index.html')
    context = {
        # TODO
    }
    return HttpResponse(template.render(context, request))

def event_index(request):
    template = loader.get_template('website/event_index.html')
    context = {
        # TODO
    }
    return HttpResponse(template.render(context, request))

def event_page(request, event_url_name):
    return HttpResponse('<h1>Page for the event</h1>')

def about(request):
    template = loader.get_template('website/about.html')
    context = {
        # TODO
    }
    return HttpResponse(template.render(context, request))

def login(request):
    return HttpResponse('login page')
