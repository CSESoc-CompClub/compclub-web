from django.db import models


class Position(models.Model):
    name = models.CharField(
            verbose_name='position name'
            )


class User(models.Model):
    zId = models.CharField(primary_key=True)
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position)
    email = models.EmailField(
            verbose_name='email address'
            )
    number = models.CharField(
            verbose_name='phone number'
            )
    is_activated = models.BooleanField()

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField()
    publish_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
    description = models.TextField()
    prerequisite = models.TextField()
    availability_period = models.TextField()

    def __str__(self):
        return self.name


class Workshop(models.Model):
    name = models.CharField()
    time = models.DateTimeField()
    description = models.TextField()
    location = models.CharField()

    def __str__(self):
        return f"{self.name} ({self.time})"


class EventAvailabiliy(models.Model):
    zId = models.ForeignKey(User)
    eventId = models.ForeignKey(Event)


class EventAssignment(models.Model):
    zId = models.ForeignKey(User)
    eventId = models.ForeignKey(Event)


class Registration(models.Model):
    eventId = models.ForeignKey(Event)
    name = models.CharField(max_length=100)
    email = models.EmailField(
            verbose_name='email address'
            )
    number = models.CharField(
            verbose_name='phone number'
            )
    date_of_birth = models.DateField()
    parent_email = models.EmailField()
    parent_number = models.CharField()

    def __str__(self):
        return f"event ID: {self.eventId} {self.name}"
