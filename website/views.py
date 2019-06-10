"""Compclub Website Views

Contains functions to render views (i.e. pages) to the user as HTTP responses.
For more information, see https://docs.djangoproject.com/en/2.1/topics/http/views/
"""
from collections import namedtuple
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError, send_mass_mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse

from smtplib import SMTPSenderRefused

from website.forms import (EventForm, RegistrationForm, VolunteerAssignForm,
                           WorkshopForm)
from website.models import Event, Workshop, Volunteer, Registration
from website.utils import generate_status_email

class EventIndex(ListView):
    """
    Render and show events page to the user. Events page shows list of current
    and future events, and how many workshops they consist of.

    Args:
        request: HTTP request header contents

    Returns:
        HTTP response containing events page
    """
    model = Event
    template_name = 'website/event_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['events_list'] = Event.objects \
            .annotate(n_workshops=Count('workshop')) \
            .filter(finish_date__gte=datetime.now()) \
            .order_by('start_date')

        return context

class EventPage(DetailView):
    """
    Render and show event detail page to the user. Event page shows specific
    and detailed information about a particular event

    Args:
        request: HTTP request header contents
        event_id: the unique ID of the event
        slug: the human-readable event name in the URL

    Returns:
        HTTP response containing the event detail page
    """
    model = Event
    context_object_name = 'event'
    template_name = 'website/event.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add event workshops to context and display first workshop location
        workshops = Workshop.objects \
            .filter(event=context['event']) \
            .order_by('date', 'start_time')
        location = workshops[0].location if len(workshops) > 0 else "TBA"
        context['workshops'] = workshops
        context['location'] = location

        # if authenticated, list workshops where user marked self as available
        if self.request.user.is_authenticated:
            user = Volunteer.objects.get(user=self.request.user)
            context['available_list'] = [workshop.id \
                for workshop in workshops \
                if user in workshop.available.all()]

        return context

    def get(self, request, event_id, slug):
        # check if url is valid
        event = get_object_or_404(Event, pk=event_id)
        if event.slug != slug:
            return redirect('website:event_page', event_id=event.pk, 
                slug=event.slug)

        return super().get(request, event_id, slug)

    def post(self, request, event_id, slug):
        if request.user.is_authenticated:
            # check if user in list of available volunteers for a workshop
            volunteer = Volunteer.objects.get(user=request.user)
            workshop_id = request.POST.get("workshop_id")
            available = Workshop.objects.get(id=workshop_id).available

            if volunteer in available.all():
                available.remove(volunteer)
            else:
                available.add(volunteer)

            return redirect('website:event_page', slug=slug, event_id=event_id)

class RegistrationPage(CreateView):
    form_class = RegistrationForm
    template_name = 'website/registration_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_form = self.get_form()
        event = Event.objects.get(id=self.kwargs['event_id'])
        registration_form.fields['event'].initial = event
        context['registration_form'] = registration_form
        context['event'] = event

        return context

    def get_success_url(self):
        return reverse('website:event_page',
            kwargs=self.kwargs)

#class RegistrationPage(View):
#    """
#    Render and show event registration form to the user. The registration form allows students
#    to register interest for a particular event.
#
#    Args:
#        request: HTTP request header contents
#        event_id: the unique ID of the event
#        slug: the human-readable event name in the URL
#
#    Returns:
#        HTTP response containing the registration form for the given event
#    """
#    def get(self, request, event_id, slug):
#        event = get_object_or_404(Event, pk=event_id)
#
#        # redirect to correct url if needed
#        if event.slug != slug:
#            return redirect(
#                'website:registration', event_id=event.pk, slug=event.slug)
#
#        registration_form = RegistrationForm()
#        registration_form.fields['event'].initial = event
#
#        context = {'registration_form': registration_form, 'event': event}
#
#        return render(request, 'website/registration_form.html', context)
#
#    def post(self, request, event_id, slug):
#        registration_form = RegistrationForm(request.POST)
#        if registration_form.is_valid():
#            registration_form.save()
#
#            return redirect('website:event_index')

@staff_member_required
def event_create(request):
    """
    Render and show an event creation form. The form allows for the creation of new events.
    Only staff members can access and see this page.

    Args:
        request: HTTP request header contents

    Returns:
        HTTP response containing the event creation form
    """
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
def volunteer_status_email_preview(request, event_id, slug):
    """
    Render and show an email preview page, and should be shown after assigning volunteers to
    workshops in an event. If a POST request is sent, an email will be sent to the listed volunteers
    whether they are assigned, on a waitlist or declined.
    Only staff members can access and see this page.

    Args:
        request: HTTP request header contents
        event_id: the unique ID (i.e. primary key) of the event being assigned
        slug: the human-readable event name in the URL

    Returns:
        HTTP response containing the email preview page
    """
    emails = generate_status_email(event_id)
    if request.method == 'POST':
        try:
            send_mass_mail(emails)
            return redirect('website:event_index')
        except BadHeaderError as e:
            print(e)
            return HttpResponse('Invalid header found')
        except SMTPSenderRefused as e:
            print(e)
            return HttpResponse('Failed to send email. The host may not have correctly configured the SMTP settings.')
    context = {'emails': emails}
    return render(request, 'website/volunteer_status_email_preview.html',
                  context)

@staff_member_required
def event_assign_volunteers(request, event_id, slug):
    """
    Render and show a volunteer assignment page. The page shows a series of forms allowing a staff
    member to assign volunteers to workshops for a particular event.
    Only staff members can access and see this page.

    Args:
        request: HTTP request header contents
        event_id: the unique ID (i.e. primary key) of the event being assigned
        slug: the human-readable event name in the URL

    Returns:
        HTTP response containing the volunteer assignment page
    """
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

@staff_member_required
def workshop_create(request, event_id, slug):
    """
    Render and show a workshop creation form page. The page shows a form allowing a staff member to
    create a new workshop for a particular event.
    Only staff members can access and see this page.

    Args:
        request: HTTP request header contents
        event_id: the ID of the event that we are making a workshop for
        slug: the human-readable event name in the URL

    Returns:
        HTTP response containing the workshop creation page
    """
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


class About(View):
    """
    Render and show the about page.

    Args:
        request: HTTP request header contents

    Returns:
        HTTP response containing the about page
    """
    def get(self, request):
        return render(request, 'website/about.html')

@login_required
def user_profile(request):
    """
    Render and show the user's profile page. Requires that the user is logged in.
    NOTE: this is minimally implemented and is currently not used

    Args:
        request: HTTP request header contents

    Returns:
        HTTP response containing the user profile page
    """
    template = loader.get_template('website/profile.html')
    return HttpResponse(template.render({}, request))
