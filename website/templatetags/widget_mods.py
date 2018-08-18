"""This module provides template tags that modifies field widgets."""
import collections

from django import template

register = template.Library()


@register.filter(name='add_attrs')
def add_attributes(field, css):
    """
    Modifies form widget attributes.

    For example, if one wants to add a placeholder attributes to
    a TextField

    original:
    {{ some_form.some_field }}
    <input name="some_form-some_field" type="text">

    {{ some_form.some_field|add_attrs:"placeholder:Foo" }}
    <input name="some_form-some_field" placeholder="Foo" type="text">

    To add a css class attribute:
    {{ some_form.some_field|add_attrs:"is-invalid" }}
    <input name="some_form-some_field" class="is-invalid" type="text">

    Mixed usage:
    {{ some_form.some_field|add_attrs:"placeholder:Foo, is-invalid" }}
    <input name="some_form-some_field" class="is-invalid" placeholder="Foo" type="text">

    Ref:
        https://gist.github.com/TimFletcher/034e799c19eb763fa859

    Args:
        field: form field
        css: css attributes, delimited by commas

    Returns:
        field that contains the extra attributes
    """
    try:
        attrs = collections.defaultdict(str, field.field.widget.attrs)
        definition = css.split(',')

        for d in definition:
            if ':' not in d:
                attrs['class'] += f" {d}"
            else:
                # split only on first occurance of ':'
                t, v = d.split(':', 1)
                attrs[t] = v
        return field.as_widget(attrs=attrs)
    except Exception:
        return field
