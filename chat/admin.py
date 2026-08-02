from django.contrib import admin

from .models import User, Room, Messages, FriendRequest
# Register your models here.

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Messages)
admin.site.register(FriendRequest)