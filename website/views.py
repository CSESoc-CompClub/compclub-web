"""Compclub Website Views

Contains functions to render views (i.e. pages) to the user as HTTP responses.
For more information, see https://docs.djangoproject.com/en/2.1/topics/http/views/
"""
from collections import namedtuple
from datetime import datetime
from django.core.mail import BadHeaderError, send_mass_mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
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
    """
    Render and show event registration form to the user. The registration form allows students
    to register interest for a particular event.

    Args:
        request: HTTP request header contents
        event_id: the unique ID of the event
        slug: the human-readable event name in the URL

    Returns:
        HTTP response containing the registration form for the given event
    """
    form_class = RegistrationForm
    template_name = 'website/registration_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        event = Event.objects.get(id=self.kwargs['event_id'])
        registration_form = self.get_form()
        registration_form.fields['event'].initial = event

        context['registration_form'] = registration_form
        context['event'] = event

        return context

    def get(self, request, event_id, slug):
        # check if url is valid
        event = get_object_or_404(Event, pk=event_id)
        if event.slug != slug:
            return redirect('website:registration', event_id=event.pk, 
                slug=event.slug)

        return super().get(request, event_id, slug)

    def get_success_url(self):
        return reverse('website:event_page', kwargs=self.kwargs)

class EventCreate(CreateView):
    """
    Render and show an event creation form. The form allows for the creation of new events.
    Only staff members can access and see this page.

    Args:
        request: HTTP request header contents

    Returns:
        HTTP response containing the event creation form
    """
    form_class = EventForm
    template_name = 'website/event_create.html'

    def get_success_url(self):
        return reverse('website:event_page', kwargs=self.kwargs)

class VolunteerStatusEmailPreview(View):
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
    template_name = 'website/volunteer_status_email_preview.html'

    def get_context_data(self, event_id):
        emails = generate_status_email(event_id)
        context = {'emails': emails}
        return context

    def get(self, request, event_id, slug):
        context = self.get_context_data(event_id)
        return render(request, self.template_name, context)

    def post(self, request, event_id, slug):
        emails = self.get_context_data(event_id)['emails']
        try:
            send_mass_mail(emails)
            return redirect('website:event_index')
        except BadHeaderError as e:
            print(e)
            return HttpResponse('Invalid header found')
        except SMTPSenderRefused as e:
            print(e)
            return HttpResponse('Failed to send email. The host may not have \
                                 correctly configured the SMTP settings.')


class EventAssignVolunteers(View):
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
    template_name = 'website/event_assign.html'

    def get_context_data(self, event_id):
        event = get_object_or_404(Event, pk=event_id)
        workshops = event.workshop.all().order_by('start_time')
        forms = [VolunteerAssignForm(initial={'workshop_id': w.id},
                                     available=w.available.all(),
                                     assignments=w.assignment.all()) \
                for w in workshops]

        WorkshopTuple = namedtuple('WorkshopTuple', ['model', 'form'])
        tuples = [WorkshopTuple(w, f) for w, f in zip(workshops, forms)]
        context = {'event': event, 'workshops': tuples}

        return context

    def get(self, request, event_id, slug):
        context = self.get_context_data(event_id)

        return render(request, self.template_name, context)

    def post(self, request, event_id, slug):
        if 'workshop_id' in request.POST:
            workshop = get_object_or_404(Workshop, pk=request.POST['workshop_id'])

            post_form = VolunteerAssignForm(request.POST,
                available=workshop.available.all(),
                assignments=workshop.assignment.all())

            if post_form.is_valid():
                post_form.save()
                return redirect('website:assign_volunteers', 
                                event_id=event_id, 
                                slug=slug)

class WorkshopCreate(CreateView):
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
    form_class = WorkshopForm
    template_name = 'website/workshop_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        event = Event.objects.get(id=self.kwargs['event_id'])
        form = self.get_form()
        form.fields['event'].initial = event

        context['workshop_form'] = form
        context['event'] = event

        return context

    def get_success_url(self):
        return reverse('website:event_page', kwargs=self.kwargs)

class About(TemplateView):
    """
    Render and show the about page.

    Args:
        request: HTTP request header contents

    Returns:
        HTTP response containing the about page
    """
    template_name = 'website/about.html'

#@login_required
#def user_profile(request):
#    """
#    Render and show the user's profile page. Requires that the user is logged in.
#    NOTE: this is minimally implemented and is currently not used
#
#    Args:
#        request: HTTP request header contents
#
#    Returns:
#        HTTP response containing the user profile page
#    """
#    template = loader.get_template('website/profile.html')
#    return HttpResponse(template.render({}, request))
