from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = 'website'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('profile/', views.user_profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('events/', views.event_index, name='event_index'),
    # TODO replace once homepage has been filled
    path('events/', RedirectView.as_view(url='/', permanent=False), name='event_index'),
    path('events/<slug:slug>-<int:event_id>/', views.event_page, name='event_page'),
    path('events/create', views.event_create, name='event_create'),
    path('about/', views.about, name='about'),
    # TODO add content to homepage
    # path('', views.index, name='index'),
    path('', views.event_index, name='index'),
]
