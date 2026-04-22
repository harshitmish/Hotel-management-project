from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from django.utils.html import format_html

from .models import Room, Booking, RoomImage
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


# 🔥 SAFE: admin_site define (taaki crash na ho)
admin_site = admin.site


# 🔥 INLINE IMAGES
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 3


# 🔥 ROOM ADMIN
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'price', 'is_available')
    search_fields = ('name',)
    list_filter = ('room_type', 'is_available')
    inlines = [RoomImageInline]
    exclude = ('image',)


# 🔥 BOOKING ADMIN
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'status', 'created_at')
    list_filter = ('status',)


# 🔥 IMAGE ADMIN
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ('room', 'preview')

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:8px;" />',
                obj.image.url
            )
        return "No Image"


# 🔥 REGISTER ALL (default admin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(RoomImage, RoomImageAdmin)

# 🔥 GOOGLE LOGIN
admin.site.register(SocialApp)
admin.site.register(Site)


# 🔥 DUPLICATE BLOCK (kept but RENAMED so no conflict)
class RoomImageInline2(admin.TabularInline):
    model = RoomImage
    extra = 3


class RoomAdmin2(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'price', 'is_available')
    search_fields = ('name',)
    list_filter = ('room_type', 'is_available')
    inlines = [RoomImageInline2]
    exclude = ('image',)


class BookingAdmin2(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'status', 'created_at')
    list_filter = ('status',)


class RoomImageAdmin2(admin.ModelAdmin):
    list_display = ('room', 'preview')

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:8px;" />',
                obj.image.url
            )
        return "No Image"


# 🔥 REGISTER (safe — admin_site == admin.site)
admin_site.register(Room, RoomAdmin)
admin_site.register(Booking, BookingAdmin)
admin_site.register(RoomImage, RoomImageAdmin)

# 🔥 GOOGLE LOGIN
admin_site.register(SocialApp)
admin_site.register(Site)