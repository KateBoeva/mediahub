from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import Collection, User, Tag, MediaItem, MediaLike, MediaComment


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_superuser', 'is_staff', 'is_active')
    list_filter = ('is_superuser', 'groups__name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_superuser',
                    'is_staff',
                    'is_active',
                    'user_permissions',
                    'groups',
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'is_active'),
            },
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('user_permissions', 'groups')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Tag)
admin.site.register(MediaItem)
admin.site.register(MediaLike)
admin.site.register(MediaComment)
admin.site.register(Collection)
