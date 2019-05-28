from django.contrib import admin
from .models import Profile, Association, Member
from .forms import MemberAdminFormset
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

# Register your models here.


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = _("Extra")
    verbose_name_plural = _("Extras")


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]


class MemberInline(admin.TabularInline):
    model = Member
    formset = MemberAdminFormset


class AssociationAdmin(admin.ModelAdmin):
    inlines = [MemberInline]
    fieldsets = [
            (_('Name of the association'), {'fields': ['name']})
    ]

admin.site.register(Profile)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Association, AssociationAdmin)
