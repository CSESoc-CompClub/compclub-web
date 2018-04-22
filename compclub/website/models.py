"""Provides models for the CompClub website."""
from django.db import models


class Position(models.Model):
    """Model representing the role of a user."""

    name = models.CharField(verbose_name='position name')


class User(models.Model):
    """Model representing a user."""

    zId = models.CharField(primary_key=True)
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position)
    email = models.EmailField(verbose_name='email address')
    number = models.CharField(verbose_name='phone number')
    is_activated = models.BooleanField()

    def __str__(self):
        """Return a string representation of a user."""
        return self.name


class Event(models.Model):
    """
    Model representing a CompClub event.

    An event can contain multiple workshops (as long as the workshops are
    within the event period.
    """

    name = models.CharField()
    start_date = models.DateField()
    finish_date = models.DateField()
    owner = models.ForeignKey(User)
    description = models.TextField(null=True)
    prerequisite = models.TextField()
    availability_period = models.TextField()

    def __str__(self):
        """Return a string representation of an event."""
        return self.name


class Workshop(models.Model):
    """Model representing a workshop in a CompClub event."""

    name = models.CharField()
    time = models.DateTimeField()
    description = models.TextField(null=True)
    location = models.CharField()

    def __str__(self):
        """Return a string representation of a workshop."""
        return f"{self.name} ({self.time})"


class EventAvailabiliy(models.Model):
    zId = models.ForeignKey(User)
    eventId = models.ForeignKey(Event)


class EventAssignment(models.Model):
    zId = models.ForeignKey(User)
    eventId = models.ForeignKey(Event)


class Registration(models.Model):
    """Model representing a student registration."""

    eventId = models.ForeignKey(Event)
    name = models.CharField(max_length=100)
    email = models.EmailField(verbose_name='email address')
    number = models.CharField(verbose_name='phone number')
    date_of_birth = models.DateField()
    parent_email = models.EmailField()
    parent_number = models.CharField()

    def __str__(self):
        """Return a string representation of a registration."""
        return f"event ID: {self.eventId} {self.name}"
