from django.urls import include, path

from . import views

urlpatterns = [
    path('events/', views.event_index, name='event_index'),
    path('events/<event_url_name>/', views.event_page, name='event_page'),
    path('about/', views.about, name='about'),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', views.login, name='signup')
]
