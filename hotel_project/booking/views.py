from django.shortcuts import render, redirect
from .models import Room, Booking, Review
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.http import JsonResponse


# 🔐 FORGOT PASSWORD
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            messages.error(request, "Email not found ❌")
            return redirect('forgot_password')

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"
        print("\nRESET LINK:", reset_link, "\n")

        messages.success(request, "Check terminal for reset link 🔗")
        return redirect('forgot_password')

    return render(request, 'booking/forgot.html')


# 🔐 RESET PASSWORD
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid link ❌")
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')

        if len(password) < 6:
            messages.error(request, "Password too short ❌")
            return redirect(request.path)

        user.set_password(password)
        user.save()
        messages.success(request, "Password reset successful ✅")
        return redirect('login')

    return render(request, 'booking/reset.html')


# 📋 MY BOOKINGS
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})


# 🏠 HOME
def home(request):
    rooms = Room.objects.all()[:3]
    return render(request, 'booking/home.html', {'rooms': rooms})


# 🏨 ROOMS (FILTER + SEARCH + RATING)
def rooms(request):
    rooms = Room.objects.all().prefetch_related('reviews')

    query = request.GET.get('q')
    if query:
        rooms = rooms.filter(name__icontains=query)

    room_type = request.GET.get('type')
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        rooms = rooms.filter(price__gte=min_price)

    if max_price:
        rooms = rooms.filter(price__lte=max_price)

    for room in rooms:
        room.avg_rating = room.reviews.aggregate(avg=Avg('rating'))['avg']

    return render(request, 'booking/rooms.html', {'rooms': rooms})


# 📅 STEP 1: DATE SELECT + OVERLAP CHECK
@login_required
def book_room(request):
    room_id = request.GET.get('room_id')

    if not room_id:
        return redirect('rooms')

    room = Room.objects.get(id=room_id)

    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        if not check_in or not check_out:
            messages.error(request, "Select dates ❌")
            return redirect(request.path + f"?room_id={room_id}")

        check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out, "%Y-%m-%d").date()

        if check_in >= check_out:
            messages.error(request, "Invalid dates ❌")
            return redirect(request.path + f"?room_id={room_id}")

        # 🔥 overlap check
        if Booking.objects.filter(
            room=room,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists():
            messages.error(request, "Already booked ❌")
            return redirect(request.path + f"?room_id={room_id}")

        request.session['check_in'] = str(check_in)
        request.session['check_out'] = str(check_out)

        return redirect(f"/book-details/?room_id={room_id}")

    return render(request, 'booking/select_date.html', {'room': room})


# 📅 STEP 2: DETAILS + VALIDATION
@login_required
def book_details(request):
    room_id = request.GET.get('room_id')

    if not room_id:
        return redirect('rooms')

    room = Room.objects.get(id=room_id)

    check_in = request.session.get('check_in')
    check_out = request.session.get('check_out')

    if not check_in or not check_out:
        return redirect(f"/book/?room_id={room_id}")

    people_range = range(1, room.capacity + 1)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        people = request.POST.get('people')

        if not people:
            messages.error(request, "Select people ❌")
            return redirect(request.path + f"?room_id={room_id}")

        people = int(people)

        if people > room.capacity:
            messages.error(request, f"Max {room.capacity} people ❌")
            return redirect(request.path + f"?room_id={room_id}")

        request.session['booking_data'] = {
            'room_id': room.id,
            'name': name,
            'phone': phone,
            'people': people,
            'id_proof': request.POST.get('id_proof'),
            'check_in': check_in,
            'check_out': check_out
        }

        return redirect('booking_summary')

    return render(request, 'booking/book_details.html', {
        'room': room,
        'people_range': people_range,
        'user': request.user
    })


# 📝 SIGNUP (FULL VALIDATION)
def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "Passwords mismatch ❌")
            return redirect('signup')

        if len(password) < 6:
            messages.error(request, "Min 6 chars ❌")
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Already registered ❌")
            return redirect('signup')

        User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, "Account created 🎉")
        return redirect('login')

    return render(request, 'booking/signup.html')


# 🔐 LOGIN (FIXED)
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('username').strip().lower()
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if not user:
            messages.error(request, "Invalid login ❌")
            return redirect('login')

        login(request, user)
        messages.success(request, "Login successful ✅")
        return redirect('home')

    return render(request, 'booking/login.html')


# 🚪 LOGOUT
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out 👋")
    return redirect('login')


# ❌ CANCEL BOOKING (SAFE)
@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.filter(id=booking_id, user=request.user).first()

    if not booking:
        messages.error(request, "Unauthorized ❌")
        return redirect('my_bookings')

    booking.delete()
    messages.success(request, "Cancelled ❌")
    return redirect('my_bookings')


# ⭐ REVIEW
@login_required
def add_review(request, room_id):
    room = Room.objects.get(id=room_id)

    if request.method == 'POST':
        Review.objects.create(
            user=request.user,
            room=room,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )
        messages.success(request, "Review added ✅")
        return redirect('rooms')

    return render(request, 'booking/add_review.html', {'room': room})


# 📄 ROOM DETAIL
def room_detail(request, room_id):
    room = Room.objects.get(id=room_id)
    reviews = room.reviews.all()

    return render(request, 'booking/room_detail.html', {
        'room': room,
        'reviews': reviews
    })


# 📋 SUMMARY
@login_required
def booking_summary(request):
    data = request.session.get('booking_data')

    if not data:
        return redirect('rooms')

    room = Room.objects.get(id=data['room_id'])

    if request.method == 'POST':
        Booking.objects.create(
            user=request.user,
            room=room,
            name=data['name'],
            phone=data['phone'],
            total_people=data['people'],
            id_proof=data['id_proof'],
            check_in=data['check_in'],
            check_out=data['check_out']
        )

        del request.session['booking_data']
        messages.success(request, "Booking confirmed 🎉")
        return redirect('my_bookings')

    return render(request, 'booking/booking_summary.html', {
        'room': room,
        'data': data
    })

#chatbot
def chatbot(request):
    msg = request.GET.get("message", "").lower()

    if not msg:
        return JsonResponse({"reply": "Hello..."})

    # 🔥 memory get
    last_intent = request.session.get("last_intent")

    # 🔥 CHEAP / BEST
    if "cheap" in msg or "best" in msg:
        room = Room.objects.order_by('price').first()

        if room:
            request.session["last_intent"] = "cheap"
            request.session["last_room"] = room.id
            return JsonResponse({"reply": f"{room.name} ₹{room.price}"})

        return JsonResponse({"reply": "No rooms"})

    # 🔥 PEOPLE (SMART MEMORY)
    elif "people" in msg:
        try:
            num = int(''.join(filter(str.isdigit, msg)))

            # 🔥 agar pehle cheap search kiya tha
            if last_intent == "cheap":
                room_id = request.session.get("last_room")
                room = Room.objects.get(id=room_id)

                if room.capacity >= num:
                    return JsonResponse({
                        "reply": f"{room.name} is perfect for {num} people 👍"
                    })
                else:
                    return JsonResponse({
                        "reply": f"{room.name} is too small ❌ Try bigger room"
                    })

            # 🔥 normal flow
            rooms = Room.objects.filter(capacity__gte=num)
            names = ", ".join([r.name for r in rooms])

            request.session["last_intent"] = "people"

            return JsonResponse({
                "reply": f"Rooms for {num} people: {names}"
            })

        except:
            return JsonResponse({"reply": "Try: 2 people"})

    # 🔥 AC
    elif "ac" in msg:
        rooms = Room.objects.filter(room_type="AC")
        names = ", ".join([r.name for r in rooms])

        request.session["last_intent"] = "ac"

        return JsonResponse({"reply": f"AC Rooms: {names}"})

    # 🔥 PRICE UNDER
    elif "under" in msg:
        try:
            price = int(''.join(filter(str.isdigit, msg)))
            rooms = Room.objects.filter(price__lte=price)
            names = ", ".join([f"{r.name} ₹{r.price}" for r in rooms])

            request.session["last_intent"] = "price"

            return JsonResponse({
                "reply": f"Rooms under ₹{price}: {names}"
            })

        except:
            return JsonResponse({"reply": "Try: under 3000"})

    # 🔥 FOLLOW-UP SMARTNESS
    elif "book" in msg and last_intent:
        return JsonResponse({
            "reply": "You can go to Rooms → select your last searched room → Book Now"
        })

    # 🔥 DEFAULT
    return JsonResponse({
        "reply": "Try: cheap room, AC, under 3000, 2 people"
    })