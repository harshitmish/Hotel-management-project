from django.urls import path
from . import views
from django.contrib import admin   # ✅ ye use karo

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.rooms, name='rooms'),
    path('book/', views.book_room, name='book_room'),

    # ✅ FIXED
    path('admin/', admin.site.urls),

    path('chatbot/', views.chatbot, name='chatbot'),

    # authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('add-review/<int:room_id>/', views.add_review, name='add_review'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('book-details/', views.book_details, name='book_details'),
    path('booking-summary/', views.booking_summary, name='booking_summary'),
    path('download-pdf/<int:booking_id>/', views.download_booking_pdf, name='download_pdf'),
]