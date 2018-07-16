from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'website'

urlpatterns = [
    path('accounts/login/', auth_views.login, {'redirect_authenticated_user': True}, name='login'),
    path('accounts/profile/', views.user_profile, name='profile'),
    path('logout/', auth_views.logout, name='logout'),
    path('events/', views.event_index, name='event_index'),
    path('events/<slug:slug>-<int:event_id>/', views.event_page, name='event_page'),
    path('about/', views.about, name='about'),
    path('', views.index, name='index'),
    path('events/<slug:slug>-<int:event_id>/Registration',views.registration,name='registration')
]
