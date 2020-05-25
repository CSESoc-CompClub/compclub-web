"""A collection of renderers for the django-content-editor."""

from django.utils.html import format_html, mark_safe
import requests


def render_rich_text(element):
    """Render a rich text element."""
    return mark_safe(element.text)


def render_download(element):
    """Render a download element."""
    return format_html(
        """
        <br/>
        <a class="btn btn-primary download-button"
           href="{}" role="button" download>
            <i class="fa fa-download"></i> Download {}
        </a>
        """,
        element.file.url,
        element.name,
    )  # noqa: E501


def render_noembed(element):
    """Render a NoEmbed element.

    This is NOT safe for use with non-admin/staff user input.
    """
    response = requests.get("https://noembed.com/embed", params={
        "url": element.url
    })

    noembed_html = response.json()["html"].strip()

    return mark_safe(
        str.format("""
        <figure class="embed-container">{}<figcaption>{}</figcaption></figure>
        """, noembed_html, element.caption)
    )


def render_lightbox(element):
    """Render an image with a lightbox."""
    return mark_safe(
        str.format("""
        <a data-fslightbox href="{0}">
            <figure class="embed-container">
                <img style="max-width: 60%; display: flex; align-self: center;" src="{0}" alt="{1}">
            <figcaption>{1}</figcaption>
            </figure>
        </a>
        """, element.file.url, element.caption)  # noqa: E501
    )
