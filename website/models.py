"""Provides models for the CompClub website."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import sys

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
    """Model representing the specific role of a volunteer type user (See Volunteer model)."""

    name = models.CharField(verbose_name='position name', max_length=50)


class Volunteer(models.Model):
    """Model representing volunteer type users."""
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name='volunteer')
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

    Three types of events exist.
    UNSW info days: No support needed. Students and volunteers can't sign up
    School_based_events: volunteer support
    UNSW_events: Volunteers and students support needed
    """

    name = models.CharField(max_length=100)
    SCHOOL = 'SE'
    UNI_INFO = 'UIE'
    UNI = 'UE'

    EVENT_TYPES = (
        (SCHOOL, 'School'),
        (UNI_INFO, 'Uni_Info'),
        (UNI, 'Uni'),
    )
    event_types = models.CharField(max_length = 3,
                                    choices = EVENT_TYPES,
                                    default = UNI,
    )
    start_date = models.DateField()
    finish_date = models.DateField()
    owner = models.ForeignKey(Volunteer, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)
    prerequisite = models.TextField()
    period = models.TextField(verbose_name='availability period')
    slug = models.SlugField(default='event', unique=False)  # url name of event


    def __str__(self):
        """Return a string representation of an event."""
        return self.name

    def hasWorkshops(self):
       if self.event_types == self.UNI_INFO:
           #print(self.event_types)
           #print(self.UNI_INFO)
           #sys.stdout.flush()
           return False
       else:
           return True

    def save(self, *args, **kwargs):
        """Override save to update slug."""
        self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)


class Workshop(models.Model):
    """Model representing a workshop in a CompClub event."""

    event = models.ForeignKey(
        Event, related_name='workshop', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField(verbose_name="start time")
    end_time = models.TimeField(verbose_name="end time")
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100)
    available = models.ManyToManyField(
        Volunteer,
        verbose_name='available volunteers',
        related_name='workshops_available')
    assigned = models.ManyToManyField(
        Volunteer,
        through='VolunteerAssignment',
        related_name='workshops_assigned')

    def unassigned(self):
        """Return a list of available volunteers who are not yet assigned/declined."""
        return list(self.available.exclude(id__in=self.assigned.all()))

    def withdrawn(self):
        """
        Return a list of volunteers who were assigned or on waitlist but then
        withdrew their availability.
        """
        assignments = list(
            self.assignment.exclude(
                status=VolunteerAssignment.DECLINED).exclude(
                    volunteer__in=self.available.all()))
        return list(map(lambda assign: assign.volunteer, assignments))

    def __str__(self):
        """Return a string representation of a workshop."""
        return f"{self.event.name}: {self.name} ({self.start_time} to {self.end_time})"


class VolunteerAssignment(models.Model):
    """Model representing an assignment of a Volunteer to a Workshop"""
    workshop = models.ForeignKey(
        Workshop, on_delete=models.CASCADE, related_name='assignment')
    volunteer = models.ForeignKey(
        Volunteer, on_delete=models.CASCADE, related_name='assignment')
    ASSIGNED = 'AS'
    WAITLIST = 'WL'
    DECLINED = 'DE'
    ASSIGN_CHOICES = (
        (ASSIGNED, 'Assigned'),
        (WAITLIST, 'Waitlist'),
        (DECLINED, 'Decline'),
    )
    status = models.CharField(max_length=2, choices=ASSIGN_CHOICES)

    class Meta:
        unique_together = ('workshop', 'volunteer')

    def __str__(self):
        status_msg = self.status
        if self.status == VolunteerAssignment.ASSIGNED:
            status_msg = 'assigned to'
        elif self.status == VolunteerAssignment.WAITLIST:
            status_msg = 'on waitlist for'
        elif self.status == VolunteerAssignment.DECLINED:
            status_msg = 'declined for'

        return f'{self.volunteer} -- {status_msg} -- {self.workshop}'


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
        return f"{self.name}"
