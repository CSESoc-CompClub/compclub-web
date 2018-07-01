from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Event, Workshop

def index(request):
    template = loader.get_template('website/index.html')
    context = {
        # TODO
    }
    return HttpResponse(template.render(context, request))


def event_index(request):
    template = loader.get_template('website/event_index.html')
    # get list of current and future events, and how many workshops they consist of
    events = Event.objects \
        .annotate(n_workshops=Count('workshop')) \
        .filter(finish_date__gte=datetime.now()) \
        .order_by('start_date')
    context = {
        'events_list': events,
    }
    return HttpResponse(template.render(context, request))


def event_page(request, event_id, slug):
    event = get_object_or_404(Event, pk=event_id)

    # redirect to correct url if needed
    if event.slug != slug:
        return redirect('website:event_page', event_id=event.pk, slug=event.slug)

    workshops = Workshop.objects.filter(event=event)
    template = loader.get_template('website/event.html')
    context = {
        'event': event,
        'workshops': workshops,
        'location': workshops[0].location,
    }
    return HttpResponse(template.render(context, request))


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
