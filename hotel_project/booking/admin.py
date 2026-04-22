from django.contrib import admin
from .models import Room, Booking, RoomImage
from django.urls import path
from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils.html import format_html
from django.contrib import admin
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

admin.site.register(SocialApp)
admin.site.register(Site)


# 🔥 CUSTOM ADMIN
class CustomAdminSite(admin.AdminSite):
    site_header = "Hotel Dashboard"

    def index(self, request, extra_context=None):
        return super().index(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        total_rooms = Room.objects.count()
        total_bookings = Booking.objects.count()

        revenue = sum([b.room.price for b in Booking.objects.all()])

        data = Booking.objects.values('check_in').annotate(count=Count('id'))

        dates = [
            x['check_in'].strftime("%d-%m") if x['check_in'] else ""
            for x in data
        ]
        counts = [x['count'] for x in data]

        context = dict(
            self.each_context(request),
            total_rooms=total_rooms,
            total_bookings=total_bookings,
            revenue=revenue,
            dates=dates,
            counts=counts,
        )

        return render(request, "admin/dashboard.html", context)


# 🔥 admin site
admin_site = CustomAdminSite(name='myadmin')


# 🔥 INLINE IMAGES
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 3


# 🔥 ROOM ADMIN (FIXED)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'price', 'is_available')
    search_fields = ('name',)
    list_filter = ('room_type', 'is_available')

    inlines = [RoomImageInline]

    # 🔥 IMPORTANT: single image field hide
    exclude = ('image',)


# 🔥 BOOKING ADMIN
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out')
    list_filter = ('check_in', 'check_out')
    search_fields = ('user__username',)


# 🔥 IMAGE ADMIN (BONUS CLEAN VIEW)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ('room', 'preview')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" style="border-radius:8px;" />', obj.image.url)
        return "No Image"
        
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'status', 'created_at')
    list_filter = ('status',)

# 🔥 REGISTER
admin_site.register(Room, RoomAdmin)
admin_site.register(Booking, BookingAdmin)
admin_site.register(RoomImage, RoomImageAdmin)

