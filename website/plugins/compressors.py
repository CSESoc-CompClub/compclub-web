"""Tools for compressing resources."""

from io import BytesIO
from PIL import Image
from django.core.files import File


def compress_image(image, return_bytes=False):
    """Convert and compress an image."""
    pillow_image = Image.open(image)
    image_bytes_io = BytesIO()
    pillow_image.thumbnail((1000, 1000), Image.ANTIALIAS)

    if pillow_image.format == "PNG":
        pillow_image.save(image_bytes_io, 'PNG', optimize=True)
    else:
        pillow_image.save(image_bytes_io, 'JPEG', quality=85)

    if return_bytes:
        return image_bytes_io

    new_image = File(image_bytes_io, name=image.name)
    return new_image
