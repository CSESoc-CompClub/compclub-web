"""Tools for modifying lists."""

from django import template

register = template.Library()


@register.filter(name='filterby')
def filterby(list_value, field_info):
    """Filter all members of the list by a field's value."""
    field_name, field_value = field_info.split(",")
    return [
        item for item in list_value if str(getattr(
            item, field_name)) == field_value]
