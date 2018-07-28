"""Provides models for the CompClub website."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify


class CustomUser(AbstractUser):
    """
    Extension of Django user model. Makes email, first and last name fields compulsory.
    Adds phone number field.
    """
    first_name = models.CharField(max_length=200, blank=False)
    last_name = models.CharField(max_length=200, blank=False)
    email = models.EmailField(blank=False)
    number = models.CharField(verbose_name="phone number", max_length=15)


class Position(models.Model):
    """Model representing the role of a user."""

    name = models.CharField(verbose_name='position name', max_length=50)


class Volunteer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    availability = models.ManyToManyField(
        'Event', related_name="availability", blank=True)
    assigned_event = models.ManyToManyField(
        'Event', related_name="assigned", blank=True)
    position = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """Return a string representation of a volunteer."""
        return f"{self.user.username} ({self.user.first_name} {self.user.last_name})"


@receiver(post_save, sender=get_user_model())
def create_or_update_volunteer(sender, instance, created, **kwargs):
    if created:
        Volunteer.objects.create(user=instance)
    instance.volunteer.save()


class Student(models.Model):
    """Model representing a student."""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    number = models.CharField(verbose_name='phone number', max_length=15)
    date_of_birth = models.DateField()
    parent_email = models.EmailField()
    parent_number = models.CharField(
        verbose_name='parent\'s phone number', max_length=15)

    def __str__(self):
        """Return a string representation of a student."""
        return self.user.first_name


class Event(models.Model):
    """
    Model representing a CompClub event.

    An event can contain multiple workshops (as long as the workshops are
    within the event period.
    """

    name = models.CharField(max_length=100)
    start_date = models.DateField()
    finish_date = models.DateField()
    owner = models.ForeignKey(Volunteer, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)
    prerequisite = models.TextField()
    period = models.TextField(verbose_name='availability period')
    slug = models.SlugField(default='event', unique=False)  # url name of event

    def save(self, *args, **kwargs):
        if not self.id:  # if this is a new event
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of an event."""
        return self.name


class Workshop(models.Model):
    """Model representing a workshop in a CompClub event."""

    event = models.ForeignKey(
        Event, related_name='workshop', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time = models.DateTimeField()
    description = models.TextField(null=True)
    location = models.CharField(max_length=100)

    def __str__(self):
        """Return a string representation of a workshop."""
        return f"{self.event.name}: {self.name} ({self.time})"


class Registration(models.Model):
    """Model representing a student registration."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(verbose_name='email address')
    number = models.CharField(verbose_name='phone number', max_length=15)
    date_of_birth = models.DateField()
    parent_email = models.EmailField()
    parent_number = models.CharField(
        verbose_name='parent\'s phone number', max_length=15)

    def __str__(self):
        """Return a string representation of a registration."""
        return f"event ID: {self.eventId} {self.name}"
