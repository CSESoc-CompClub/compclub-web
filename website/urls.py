"""Compclub Website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView
from django.contrib.admin.views.decorators import staff_member_required

from . import views

app_name = 'website' # URL namespace

urlpatterns = [
    path( # login view
        'login/',
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name='login'),
    path('profile/', views.user_profile, name='profile'), # profile page view (currently not used)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('events/', views.event_index, name='event_index'),
    # TODO: replace once homepage has been filled
    path( # events view
        'events/',
        RedirectView.as_view(url='/', permanent=False), # currently, homepage is also events page
        name='event_index'),
    path( # event detail view
        'events/<slug:slug>-<int:event_id>/',
        views.EventPage.as_view(),
        name='event_page'),
    path('events/create', 
          staff_member_required(views.EventCreate.as_view()),
          name='event_create'), # create event view
    path('about/', views.About.as_view(), name='about'), # about page view
    # TODO add content to homepage
    path('', views.EventIndex.as_view(), name='index'), # homepage view
    path('events/<slug:slug>-<int:event_id>/status-email-preview', # email preview page
        staff_member_required(views.VolunteerStatusEmailPreview.as_view()),
        name='volunteer_email_preview'),
    path(
        'events/<slug:slug>-<int:event_id>/registration', # event regitration view (for students)
        views.RegistrationPage.as_view(),
        name='registration'),
    path(
        'events/<slug:slug>-<int:event_id>/assign-volunteers', # event volunteer assignment page
        views.event_assign_volunteers,
        name='assign_volunteers'),
    path('events/<slug:slug>-<int:event_id>/workshop_create', # event workshop creation page
        staff_member_required(views.WorkshopCreate.as_view()),
        name="workshop_create")
]
