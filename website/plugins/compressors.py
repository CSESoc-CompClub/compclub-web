"""Tools for compressing resources."""

from io import BytesIO
from PIL import Image
from django.core.files import File


def compress_image(image):
    """Convert and compress an image."""
    pillow_image = Image.open(image)
    pillow_image.thumbnail((1000, 1000), Image.ANTIALIAS)

    image_bytes_io = BytesIO()
    pillow_image.save(image_bytes_io, 'JPEG', quality=85)
    new_image = File(image_bytes_io, name=image.name)
    return new_image
