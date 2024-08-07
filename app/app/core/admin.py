""" 
Django admin customization.
"""

from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin page for the User model."""
    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name', 'id']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'image',)
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name',
                'last_name',
                'email',
                'password1',
                'password2',
                'bio',
                'contact_me',
                'is_active',
                'is_staff',
                'is_superuser',
                'image',
            ),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Article)
admin.site.register(models.Topic)
admin.site.register(models.Comment)
admin.site.register(models.Like)
