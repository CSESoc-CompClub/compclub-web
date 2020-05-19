"""
Compclub URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/

Please add new views for the compclub website in website.urls
"""
from django.contrib import admin
from django.urls import include, path

# Compclub website URLs should be included in website.urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
]
