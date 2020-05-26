"""
Compclub Website URL configuration.

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.urls import path, include

from . import views

app_name = 'website'  # URL namespace

urlpatterns = [
    path('login/',
         auth_views.LoginView.as_view(redirect_authenticated_user=True),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.Index.as_view(), name='index'),
    path(
        'events/',
        views.EventIndex.as_view(),
        name='event_index'),
    path('events/<slug:slug>-<int:event_id>/',
         views.EventPage.as_view(),
         name='event_page'),
    path('events/create',
         staff_member_required(views.EventCreate.as_view()),
         name='event_create'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('events/<slug:slug>-<int:event_id>/status-email-preview',
         staff_member_required(views.VolunteerStatusEmailPreview.as_view()),
         name='volunteer_email_preview'),
    path('events/<slug:slug>-<int:event_id>/registration',
         views.RegistrationPage.as_view(),
         name='registration'),
    path('events/<slug:slug>-<int:event_id>/assign-volunteers',
         staff_member_required(views.EventAssignVolunteers.as_view()),
         name='assign_volunteers'),
    path('events/<slug:slug>-<int:event_id>/workshop_create',
         staff_member_required(views.WorkshopCreate.as_view()),
         name="workshop_create"),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # path('profile/',
    #     views.user_profile,
    #     name='profile'), # profile page view (currently not used)
]

# Nginx will serve the media root in production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
