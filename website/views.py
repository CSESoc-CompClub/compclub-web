from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.db.models import Count
from website.forms import EventForm, WorkshopForm, RegistrationForm
from website.models import Event, Workshop


def index(request):
    return render(request, 'website/index.html')


def event_index(request):
    # get list of current and future events, and how many workshops they consist of
    events = Event.objects \
        .annotate(n_workshops=Count('workshop')) \
        .filter(finish_date__gte=datetime.now()) \
        .order_by('start_date')
    context = {
        'events_list': events,
    }
    return render(request, 'website/event_index.html', context)


def event_page(request, event_id, slug):
    event = get_object_or_404(Event, pk=event_id)
    # redirect to correct url if needed
    if event.slug != slug:
        return redirect('website:event_page', event_id=event.pk, slug=event.slug)

    workshops = Workshop.objects.filter(event=event)
    context = {
        'event': event,
        'workshops': workshops,
        'location': workshops[0].location,
    }
    return render(request, 'website/event.html', context)


def registration(request, event_id, slug):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        registration_form = RegistrationForm(request.POST, prefix='registration_form')
        if all([registration_form.is_valid()]):
            registration_form.save()
            return redirect('website:event_index')
        else:
            print('=================== invalid form =====================')
    else:
        registration_form = RegistrationForm(prefix='registration_form')
        registration_form.fields['event'].initial = event
        context = {'registration_form': registration_form, 'event': event}
        return render(request, 'website/registration_form.html', context)


@staff_member_required
def event_create(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, prefix='event_form')
        workshop_form = WorkshopForm(request.POST, prefix='workshop_form')
        if all([event_form.is_valid(), workshop_form.is_valid()]):
            event = event_form.save()
            workshop = workshop_form.save(commit=False)
            workshop.event = event
            workshop.save()
            return redirect('website:event_index')
    else:
        event_form = EventForm(prefix='event_form')
        workshop_form = WorkshopForm(prefix='workshop_form')

    context = {'event_form': event_form, 'workshop_form': workshop_form}
    return render(request, 'website/event_create.html', context)


@staff_member_required
def signups(request):
    events = Event.objects.all().order_by('start_date')
    context = {'events': events}
    return render(request, 'website/signups.html', context)


def about(request):
    return render(request, 'website/about.html')


@login_required
def user_profile(request):
    template = loader.get_template('website/profile.html')
    return HttpResponse(template.render({}, request))
