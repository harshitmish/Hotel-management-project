from django.shortcuts import render, redirect
from .models import Room, Booking
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})



def home(request):
    return render(request, 'booking/home.html')


def rooms(request):
    rooms = Room.objects.all()
    return render(request, 'booking/rooms.html', {'rooms': rooms})


# 🔐 LOGIN REQUIRED
@login_required
def book_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        date = request.POST.get('date')

        room = Room.objects.get(id=room_id)

        # ❌ Already booked check
        if Booking.objects.filter(room=room, date=date).exists():
            messages.error(request, "Room already booked!")
            return redirect('book_room')

        # ✅ Save booking (user se link)
        Booking.objects.create(
            user=request.user,
            room=room,
            date=date
        )

        messages.success(request, "Room booked successfully!")
        return redirect('book_room')

    # 🔥 Available rooms logic
    selected_date = request.GET.get('date')

    if selected_date:
        booked_rooms = Booking.objects.filter(date=selected_date).values_list('room_id', flat=True)
        rooms = Room.objects.exclude(id__in=booked_rooms)
    else:
        rooms = Room.objects.all()

    return render(request, 'booking/booking.html', {'rooms': rooms})


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'booking/signup.html', {
                'error': 'Username already exists'
            })

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'booking/signup.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'booking/login.html', {'error': 'Invalid credentials'})

    return render(request, 'booking/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')