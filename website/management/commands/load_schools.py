"""Management command to load school data into database."""

import csv
from itertools import islice
from os import path

from django.core.management.base import BaseCommand
from django.db import transaction

from website.models import School


class Command(BaseCommand):
    """Management command for loading school data."""

    help = 'Load school data into database'

    def add_arguments(self, parser):
        """Add argument to delete all exisiting data from the database."""
        parser.add_argument(
            'csv_to_import',
            action='store',
            help='Location of the CSV to import')
        parser.add_argument(
            '--clean',
            action='store_true',
            dest='clean',
            help='Delete existing data before adding school data')

    def handle(self, *args, **options):  # noqa: D102
        schools = None
        filename = path.abspath(options["csv_to_import"])

        with transaction.atomic():
            if options['clean']:
                self.stdout.write(
                    'Cleaning existing schools from the database')
                School.objects.all().delete()
            try:
                with open(filename, "r") as fp:
                    csvreader = list(csv.DictReader(fp, dialect='unix'))
                    schools = (
                        School(name=school["School Name"],
                               region=school["Region"])
                        for school in csvreader)
            except FileNotFoundError as err:
                self.stderr.write(self.style.ERROR(
                    f"Couldn't open the file {filename}"))
                raise err

            batch_size = 100
            number_complete = 0
            while True:
                school_objs = list(islice(schools, batch_size))
                if not school_objs:
                    break
                School.objects.bulk_create(school_objs, batch_size)
                number_complete += len(school_objs)
                self.stdout.write(
                    f'Loaded {number_complete} schools.')

            self.stdout.write(self.style.SUCCESS(
                f'Loaded all {number_complete} schools.'))
