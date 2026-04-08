from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.rooms, name='rooms'),
    path('book/', views.book_room, name='book_room'),
]