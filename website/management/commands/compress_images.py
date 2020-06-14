"""Commands for compressing images."""

from website.plugins import compressors
from django.core.management.base import BaseCommand

import glob
from os import path


class Command(BaseCommand):
    """Management command for compressing collected static images."""

    help = 'Compress collected static images'

    def add_arguments(self, parser):
        """Add argument to delete all exisiting data from the database."""
        parser.add_argument(
            'collected_static_dir',
            action='store',
            help='Location of the COLLECTED static files')

    def handle(self, *args, **options):  # noqa: D102
        self.stdout.write('\nStarting image compression.')

        static_dir = path.abspath(options["collected_static_dir"])
        valid_image_exts = ["png", "jpeg", "jpg"]

        for ext in valid_image_exts:
            files = glob.glob(static_dir + f"/**/*.{ext}",
                              recursive=True)

            self.stdout.write(f'Found {len(files)} .{ext} files')
            for image in files:
                self.stdout.write(f'Compressing {image}')
                new_image = compressors.compress_image(
                    image, return_bytes=True)

                with open(image, "wb") as f:
                    f.write(new_image.getbuffer())

            self.stdout.write(self.style.SUCCESS(
                f'Compressed {len(files)} .{ext} files'))
