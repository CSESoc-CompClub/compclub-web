"""Django admin panel."""

from content_editor.admin import ContentEditor, ContentEditorInline
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models

from website.models import (CustomUser, Download, Event, NoEmbed, Registration,
                            RichText, Workshop,
                            LightBox, Student, School)


# @admin.register(VolunteerAssignment)
# class VolunteerAssignmentAdmin(admin.ModelAdmin):  # noqa: D101
#     pass


# class VolunteerInline(admin.StackedInline):
#     """Show volunteer admin form with the user form."""

#     model = Volunteer
#     can_delete = False
#     verbose_name_plural = "volunteer"
#     fk_name = "user"


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Custom user settings and configuration page in the admin panel."""

    # inlines = (VolunteerInline, )

    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': ('first_name', 'last_name', 'username', 'password1',
                   'password2', 'email'),
    }), )

    def get_inline_instances(self, request, obj=None):  # noqa: D102
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class RichTextarea(forms.Textarea):
    """Rich text area entry from django-content-editor."""

    def __init__(self, attrs=None):
        """
        Provide instance of rich text area.

        Provide class so that the code in plugin_ckeditor knows which text
        areas  should be enhanced with a rich text control.
        """
        default_attrs = {'class': 'richtext'}
        if attrs:
            default_attrs.update(attrs)
        super(RichTextarea, self).__init__(default_attrs)


class RichTextInline(ContentEditorInline):
    """Rich text inline field from django-content-editor."""

    model = RichText
    formfield_overrides = {
        models.TextField: {'widget': RichTextarea},
    }
    regions = ['main']  # We only want rich texts in "main" region.

    class Media:
        """Provides CKEditor to the fields."""

        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/ckeditor/4.12.1/ckeditor.js',  # noqa: E501
            'website/js/content-editor-plugins/plugin_ckeditor.js',
        )


@admin.register(Event)
class EventAdmin(ContentEditor):
    """Provides a pretty interface for editing content using django-content-editor."""  # noqa: E501

    inlines = [
        RichTextInline,
        ContentEditorInline.create(model=Download),
        ContentEditorInline.create(model=NoEmbed),
        ContentEditorInline.create(model=LightBox)
    ]


admin.site.register(Workshop)
admin.site.register(Registration)
admin.site.register(Student)
admin.site.register(School)
