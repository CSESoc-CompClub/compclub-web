from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from website.models import (CustomUser, Event, Registration, Volunteer,
                            VolunteerAssignment, Workshop)


@admin.register(VolunteerAssignment)
class VolunteerAssignmentAdmin(admin.ModelAdmin):
    pass


class VolunteerInline(admin.StackedInline):
    model = Volunteer
    can_delete = False
    verbose_name_plural = "volunteer"
    fk_name = "user"


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (VolunteerInline, )

    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': ('first_name', 'last_name', 'username', 'password1',
                   'password2', 'email', 'number'),
    }), )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(Event)
admin.site.register(Workshop)
admin.site.register(Registration)
