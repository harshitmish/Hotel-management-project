from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from django.utils.html import format_html

from .models import Room, Booking, RoomImage
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


# 🔥 SAFE: admin_site define (same as default, no conflict)
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


# 🔥 REGISTER ALL (ONLY ONCE)
admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(RoomImage, RoomImageAdmin)


# 🔥 DUPLICATE BLOCK (safe — NOT registered, no conflict)
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


# ❌ REMOVED duplicate register (yahi crash ka reason tha)
# admin_site.register(...)
# admin_site.register(...)