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
from django.conf.urls import handler404, handler500
from django.views.generic.base import RedirectView

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
        views.event_page,
        name='event_page'),
    path('events/create', views.event_create, name='event_create'), # create event view
    path('about/', views.about, name='about'), # about page view
    # TODO add content to homepage
    # path('', views.index, name='index'),
    path('', views.event_index, name='index'), # homepage view
    path(
        'events/<slug:slug>-<int:event_id>/status-email-preview', # email preview page
        views.volunteer_status_email_preview,
        name='volunteer_email_preview'),
    path(
        'events/<slug:slug>-<int:event_id>/registration', # event regitration view (for students)
        views.registration,
        name='registration'),
    path(
        'events/<slug:slug>-<int:event_id>/assign-volunteers', # event volunteer assignment page
        views.event_assign_volunteers,
        name='assign_volunteers'),
    path(
        'events/<slug:slug>-<int:event_id>/workshop_create', # event workshop creation page
        views.workshop_create,
        name="workshop_create")
]

handler404 = 'views.handler404'
