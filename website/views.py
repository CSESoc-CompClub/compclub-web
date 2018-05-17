from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required


def index(request):
    template = loader.get_template('website/index.html')
    context = {
        # TODO
    }
    print("Potato")
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


@login_required
def user_profile(request):
    template = loader.get_template('website/profile.html')
    return HttpResponse(template.render({}, request))
