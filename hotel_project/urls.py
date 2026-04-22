from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hotel_project.booking.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),   # ✅ yaha change
    path('', include('hotel_project.booking.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)