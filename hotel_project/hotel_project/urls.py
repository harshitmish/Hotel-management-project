from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler500
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hotel_project.booking.urls')),

def custom_500(request):
    import traceback
    return HttpResponse(traceback.format_exc())
    
handler500 = custom_500
