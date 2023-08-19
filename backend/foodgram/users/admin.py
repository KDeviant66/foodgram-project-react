from django.contrib import admin
from users.models import Follow, User


class UserADmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email'
    )
    list_filter = ('first_name', 'email')


class SubscribeADmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
    search_fields = ('following__email',
                     'following__username',
                     )
    # list_filter = ('following__username', 'user__username')


admin.site.register(User, UserADmin)
admin.site.register(Follow, SubscribeADmin)
