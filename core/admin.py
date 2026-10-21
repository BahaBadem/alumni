from django.contrib import admin
from .models import UserProfile, Announcement, JobPosting, Application


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


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company_name', 'employment_type', 'location', 'is_active', 'deadline', 'created_at')
    search_fields = ('title', 'company_name', 'description', 'location')
    list_filter = ('employment_type', 'is_active', 'deadline', 'created_at')
    list_editable = ('is_active',)
    ordering = ('-created_at',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'applicant', 'status', 'created_at')
    search_fields = ('job__title', 'job__company_name', 'applicant__name', 'cover_letter')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    ordering = ('-created_at',)
