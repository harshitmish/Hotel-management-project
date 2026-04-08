from django.shortcuts import render, redirect
from .models import Room, Booking
from django.contrib import messages
from datetime import date as today_date

from django.http import HttpResponse

def home(request):
    return render(request, 'booking/home.html')

def rooms(request):
    rooms = Room.objects.all()
    return render(request, 'booking/rooms.html', {'rooms': rooms})

def book_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        room_id = request.POST.get('room')
        date = request.POST.get('date')

        room = Room.objects.get(id=room_id)

        # ✅ Pehle check karo
        if Booking.objects.filter(room=room, date=date).exists():
            messages.error(request, "Room already booked!")
            return redirect('book_room')

        # ✅ Phir save karo
        Booking.objects.create(
            name=name,
            room=room,
            date=date
        )

        messages.success(request, "Room booked successfully!")
        return redirect('book_room')

    rooms = Room.objects.all()
    return render(request, 'booking/booking.html', {'rooms': rooms})



def book_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        room_id = request.POST.get('room')
        date = request.POST.get('date')

        room = Room.objects.get(id=room_id)

        if Booking.objects.filter(room=room, date=date).exists():
            messages.error(request, "Room already booked!")
            return redirect('book_room')

        Booking.objects.create(
            name=name,
            room=room,
            date=date
        )

        messages.success(request, "Room booked successfully!")
        return redirect('book_room')

    # 🔥 ONLY AVAILABLE ROOMS LOGIC
    selected_date = request.GET.get('date')

    if selected_date:
        booked_rooms = Booking.objects.filter(date=selected_date).values_list('room_id', flat=True)
        rooms = Room.objects.exclude(id__in=booked_rooms)
    else:
        rooms = Room.objects.all()

    return render(request, 'booking/booking.html', {'rooms': rooms})