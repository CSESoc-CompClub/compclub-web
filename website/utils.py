from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.conf import settings

from website.models import Event, Volunteer, Workshop

STATUS_EMAIL_SUBJECT = "Your Assignment For Event \"{event}\""
STATUS_EMAIL_BASE = """
Hello {recipient},

Your current assignments for {event} is as follows:

{body}

Regards,
CompClub Team
"""
STATUS_EMAIL_WORKSHOP_FMT = \
    "{workshop_name}({start_time}-{end_time}): {status}\n"


def generate_status_email(event_id,
                          subject=STATUS_EMAIL_SUBJECT,
                          base=STATUS_EMAIL_BASE,
                          workshop_fmt=STATUS_EMAIL_WORKSHOP_FMT,
                          from_email=settings.EMAIL):
    """
    Generate workshop assignment status for volunteers.

    Args:
        event_id: id of event to generate email for
        subject: common subject for emails, with `event` as named parameters
        base: base template for the body of the email, with `recipient`,
              `event` and `body` as named parameters
        workshop_fmt: workshop description format, with `workshop_name`,
                      `start_time`, `end_time` and `status` as named parameters

    Returns:
        list of emails in the following format:
            [(subject, message, from_email, [recipient.email])]

    """
    event = get_object_or_404(Event, pk=event_id)
    recipients = Volunteer.objects \
        .filter(assignment__workshop__event=event) \
        .prefetch_related(
            Prefetch(
                'workshops_assigned',
                queryset=Workshop.objects.filter(event=event)
            ),
            'assignment'
        ) \
        .select_related('user')
    subject = subject.format(event=event.name)
    emails = []
    for recipient in recipients:
        workshop_msg = str()
        for assignment in recipient.assignment.filter(
                workshop__event=event).order_by('workshop__name'):
            workshop_msg += workshop_fmt.format(
                workshop_name=assignment.workshop.name,
                start_time=assignment.workshop.start_time,
                end_time=assignment.workshop.end_time,
                status=assignment.get_status_display())
        formatted_message = base.format(
            recipient=recipient.user.first_name,
            event=event.name,
            body=workshop_msg)
        data_tuple = (subject, formatted_message, from_email,
                      [recipient.user.email])
        emails.append(data_tuple)
    return emails
