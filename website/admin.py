"""Django admin panel."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from website.models import (CustomUser, Event, Registration, Volunteer,
                            VolunteerAssignment, Workshop)


@admin.register(VolunteerAssignment)
class VolunteerAssignmentAdmin(admin.ModelAdmin):  # noqa: D101
    pass


class VolunteerInline(admin.StackedInline):
    """Show volunteer admin form with the user form."""

    model = Volunteer
    can_delete = False
    verbose_name_plural = "volunteer"
    fk_name = "user"


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Custom user settings and configuration page in the admin panel."""

    inlines = (VolunteerInline, )

    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': ('first_name', 'last_name', 'username', 'password1',
                   'password2', 'email', 'number'),
    }), )

    def get_inline_instances(self, request, obj=None):  # noqa: D102
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(Event)
admin.site.register(Workshop)
admin.site.register(Registration)
