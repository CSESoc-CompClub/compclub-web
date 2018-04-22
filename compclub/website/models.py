from django.db import models


class Position(models.Model):
    name = models.CharField('position name')


class User(models.Model):
    zId = models.CharField(primary_key=True)
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position)
    email = models.EmailField('email address')
    number = models.CharField('phone number')
    is_activated = models.BooleanField()


class Event(models.Model):
    name = models.CharField()
    publish_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
    description = models.TextField()
    prerequisite = models.TextField()
    availability_period = models.TextField()


class WorkShops(models.Model):
    name = models.CharField()
    time = models.DateTimeField()
    description = models.TextField()
    location = models.CharField()


class EventAvailabiliy(models.Model):
    zId = models.ForeignKey(User)
    eventId = models.ForeignKey(Event)


class EventAssignment(models.Model):
    zId = models.ForeignKey(User)
    eventId = models.ForeignKey(Event)


class Registration(models.Model):
    eventId = models.ForeignKey(Event)
    name = models.CharField(max_length=100)
    email = models.EmailField('email address')
    number = models.CharField('phone number')
    date_of_birth = models.DateField()
    parent_email = models.EmailField()
    parent_number = models.CharField()
