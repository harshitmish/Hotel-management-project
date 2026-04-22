from django.contrib import admin 
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from django.utils.html import format_html

from django.contrib import admin
from .models import Room, Booking, RoomImage
from django.utils.html import format_html

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


# 🔥 SAFE FALLBACK (taaki crash na ho)
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


# 🔥 REGISTER ALL
admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(RoomImage, RoomImageAdmin)

# 🔥 GOOGLE LOGIN
admin.site.register(SocialApp)
admin.site.register(Site)


# 🔥 INLINE IMAGES (duplicate - DISABLED)
class RoomImageInline_DUP(admin.TabularInline):
    model = RoomImage
    extra = 3


# 🔥 ROOM ADMIN (duplicate - DISABLED)
class RoomAdmin_DUP(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'price', 'is_available')
    search_fields = ('name',)
    list_filter = ('room_type', 'is_available')
    inlines = [RoomImageInline_DUP]
    exclude = ('image',)


# 🔥 BOOKING ADMIN (duplicate - DISABLED)
class BookingAdmin_DUP(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'status', 'created_at')
    list_filter = ('status',)


# 🔥 IMAGE ADMIN (duplicate - DISABLED)
class RoomImageAdmin_DUP(admin.ModelAdmin):
    list_display = ('room', 'preview')

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:8px;" />',
                obj.image.url
            )
        return "No Image"


# 🔥 REGISTER (custom block - SAFE, no crash)
# (ab ye bhi same admin.site pe hi point karega)
admin_site.register(Room, RoomAdmin)
admin_site.register(Booking, BookingAdmin)
admin_site.register(RoomImage, RoomImageAdmin)

# 🔥 GOOGLE LOGIN
admin_site.register(SocialApp)
admin_site.register(Site)