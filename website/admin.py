from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser, Event, Volunteer, Workshop


class UserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name' , 'last_name', 'email')

# Register your models here.
class VolunteerInline(admin.StackedInline):
    model = Volunteer
    can_delete = False
    verbose_name_plural = "volunteer"
    fk_name = "user"


class CustomUserAdmin(BaseUserAdmin):
    # add_form = UserCreateForm
    inlines = (VolunteerInline, )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'password1', 'password2', 'email', 'number'),
        }),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Event)
admin.site.register(Workshop)
