from django.contrib import admin
from .models import UserProfile, Announcement


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school', 'city', 'birth_date', 'created_at')
    search_fields = ('name', 'school', 'city')
    list_filter = ('school', 'city', 'created_at')
    ordering = ('-created_at',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'author', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'author')
    list_filter = ('category', 'is_active', 'created_at')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
