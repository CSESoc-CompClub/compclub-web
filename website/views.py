from collections import namedtuple
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError, send_mass_mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from website.forms import (EventForm, RegistrationForm, VolunteerAssignForm,
                           WorkshopForm)
from website.models import Event, Workshop, Volunteer
from website.utils import generate_status_email


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
        return redirect(
            'website:event_page', event_id=event.pk, slug=event.slug)

    workshops = Workshop.objects.filter(event=event).order_by(
        'date', 'start_time')
    template = loader.get_template('website/event.html')
    
    # Volunteers can see the "Available" Column after login
    if request.user.is_authenticated:
        request_user = request.user
        request_volunteer = Volunteer.objects.get(user=request_user)
        available_list = []
        for workshop in workshops:
            if request_volunteer in workshop.available.all():
                available_list.append(workshop.id)        
    # After Clicking the button in "Available" Column
        if request.method == "POST":
            workshop_id = request.POST.get("workshop_id")
            selected_workshop = Workshop.objects.get(id=workshop_id)
            if request_volunteer in selected_workshop.available.all():
                selected_workshop.available.remove(request_volunteer)
                
            else:
                selected_workshop.available.add(request_volunteer)

            return redirect('website:event_page',slug=slug,event_id=event_id)  
  
        context = {
            'event': event,
            'workshops': workshops,
            'location': workshops[0].location if len(workshops) > 0 else "TBA",
            'available_list':available_list
        }        

        return render(request, 'website/event.html', context)
    else:
        context = {
            'event': event,
            'workshops': workshops,
            'location': workshops[0].location if len(workshops) > 0 else "TBA",
        }        
            
        return HttpResponse(template.render(context, request))

def registration(request, event_id, slug):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        registration_form = RegistrationForm(request.POST)
        if registration_form.is_valid():
            registration_form.save()
            return redirect('website:event_index')
    else:
        registration_form = RegistrationForm()
        registration_form.fields['event'].initial = event

    context = {'registration_form': registration_form, 'event': event}
    return render(request, 'website/registration_form.html', context)


@staff_member_required
def event_create(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, prefix='event_form')
        if event_form.is_valid():
            event_form.save()
            return redirect('website:event_index')
    else:
        event_form = EventForm(prefix='event_form')

    context = {'event_form': event_form}
    return render(request, 'website/event_create.html', context)


@staff_member_required
def volunteer_status_email_preview(request, pk, slug):
    emails = generate_status_email(pk)
    if request.method == 'POST':
        try:
            send_mass_mail(emails)
            return redirect('website:event_index')
        except BadHeaderError:
            return HttpResponse('Invalid header found')
    context = {'emails': emails}
    return render(request, 'website/volunteer_status_email_preview.html',
                  context)


def event_assign_volunteers(request, event_id, slug):
    post_form = None
    if request.method == 'POST' and 'workshop_id' in request.POST:
        workshop = get_object_or_404(Workshop, pk=request.POST['workshop_id'])
        post_form = VolunteerAssignForm(
            request.POST,
            available=workshop.available.all(),
            assignments=workshop.assignment.all())
        if post_form.is_valid():
            post_form.save()
            return redirect(
                'website:assign_volunteers', event_id=event_id, slug=slug)
        # if form is not valid then display errors on relevant form

    event = get_object_or_404(Event, pk=event_id)
    workshops = event.workshop.all().order_by('start_time')

    # Generate forms for each workshop
    forms = []
    for w in workshops:
        if post_form is not None and w.id == post_form.cleaned_data[
                'workshop_id']:
            forms.append(post_form)  # use POSTed form
        else:
            forms.append(
                VolunteerAssignForm(
                    initial={'workshop_id': w.id},
                    available=w.available.all(),
                    assignments=w.assignment.all()))

    # zip Workshop and corresponding Form into namedtuple
    WorkshopTuple = namedtuple('WorkshopTuple', ['model', 'form'])
    tuples = [WorkshopTuple(w, f) for w, f in zip(workshops, forms)]
    context = {'event': event, 'workshops': tuples}
    return render(request, 'website/event_assign.html', context)

def workshop_create(request, event_id, slug):
    if request.method == 'POST':
        workshop_form = WorkshopForm(request.POST, prefix='workshop_form')
        if workshop_form.is_valid():
            workshop_form.save()
            return redirect('website:event_page', slug=slug, event_id=event_id)
    else:
        workshop_form = WorkshopForm(prefix='workshop_form')
        workshop_form['event'].initial = get_object_or_404(Event, pk=event_id)

    context = {
        'workshop_form': workshop_form,
        'event': get_object_or_404(Event, pk=event_id)
    }
    return render(request, 'website/workshop_create.html', context)


def about(request):
    return render(request, 'website/about.html')


@login_required
def user_profile(request):
    template = loader.get_template('website/profile.html')
    return HttpResponse(template.render({}, request))
