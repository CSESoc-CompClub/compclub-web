'''Management command to load dummy data into database.'''
from datetime import datetime, timedelta, date, time
import pytz
from django.core.management.base import BaseCommand
from django.db import transaction
from website.models import Workshop, Event

LOCAL_TZ = pytz.timezone('Australia/Sydney')
def local2utc(local_datetime: datetime) -> datetime:
    '''Converts local datetime to utc'''
    return LOCAL_TZ.localize(local_datetime).astimezone(pytz.utc)


def make_event(name, days_from_now, n_week, workshop_time: time, description,
               prereq, period, location):
    '''Create event and associated weekly-occuring workshops

    Args:
        name: the name of the event
        days_from_now: the days between today and the first workshop
        n_week: the number of weeks the event will run for
        workshop_time: the local time of the start of each workshop
        description: event description
        prereq: description of event prerequisites
        period: the event period
        location: the location of each workshop
    Returns:
        the created Event
    '''
    start_date = date.today() + timedelta(days=days_from_now)
    finish_date = start_date + timedelta(days=n_week*7)

    start_dt = datetime.combine(start_date, time.min)
    finish_dt = datetime.combine(finish_date, time.min)

    # generate weekly workshop times
    workshop_times = []
    wkshop_time = datetime.combine(start_date, workshop_time)
    while wkshop_time < finish_dt:
        workshop_times.append(wkshop_time)
        wkshop_time += timedelta(days=7)

    assert len(workshop_times) == n_week

    event = Event(
        name=name,
        start_date=local2utc(start_dt),
        finish_date=local2utc(finish_dt),
        description=description,
        prerequisite=prereq,
        period=period
    )
    event.save()

    # create workshops for each time
    workshops = []
    for i, w_time in enumerate(workshop_times):
        workshops.append(Workshop(
            event=event,
            name=f'Workshop #{i+1}',
            time=local2utc(w_time),
            location=location
        ))
    for workshop in workshops:
        workshop.save()
    return event


class Command(BaseCommand):
    '''
    Management command for loading dummy data
    '''
    help = 'Load dummy event and workshop objects into database'

    def add_arguments(self, parser):
        # Optional argument to delete all exisiting data from the database
        parser.add_argument(
            '--clean',
            action='store_true',
            dest='clean',
            help='Delete exisiting data before adding dummy data'
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options['clean']:
                Event.objects.all().delete()
                Workshop.objects.all().delete()
            make_event(
                'Test: single-workshop event',
                10,
                1,
                time(10, 0), # 10:00 local time
                'Learn how to <something> in 3 hours!',
                'No prior programming experience required',
                '3 hours?',
                'UNSW K17 chi lab',
            )

            make_event(
                'Test: Intro to Programming',
                15,
                6,
                time(16, 0), # 16:00 local time
                'Learn how to code and make programs using the Python programming language',
                'No prior programming experience required',
                '2 hours?',
                'UNSW K17 oud lab'
            )

            make_event(
                'Test: Advanced Web Development',
                28,
                7,
                time(16, 0),
                'Learn how to make full-scale web apps with Django',
                'Experience in web design (HTML,CSS,JavaScript) and coding in Python',
                '2 hours',
                'UNSW K17 lyre lab'
            )

        self.stdout.write(self.style.SUCCESS('Loaded.'))
