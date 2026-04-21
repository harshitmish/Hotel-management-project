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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from django.core.mail import send_mail
from django.http import HttpResponse
import random
from django.conf import settings
from .models import OTP
from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMessage
from io import BytesIO

def generate_pdf(booking):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("HOTEL INVOICE", styles['Title']))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Name: {booking.name}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {booking.phone}", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [
        ["Room", booking.room.name],
        ["Check-in", str(booking.check_in)],
        ["Check-out", str(booking.check_out)],
        ["People", str(booking.total_people)],
    ]

    table = Table(data)
    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


@login_required
def download_booking_pdf(request, booking_id):
    booking = Booking.objects.get(id=booking_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    # 🧾 TITLE
    elements.append(Paragraph("HOTEL INVOICE", styles['Title']))
    elements.append(Spacer(1, 20))

    # 🧑 CUSTOMER DETAILS
    elements.append(Paragraph(f"<b>Name:</b> {booking.name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Phone:</b> {booking.phone}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # 🏨 BOOKING DETAILS TABLE
    data = [
        ["Field", "Details"],
        ["Room", booking.room.name],
        ["Check-in", str(booking.check_in)],
        ["Check-out", str(booking.check_out)],
        ["Total People", str(booking.total_people)],
        ["Status", booking.status],
    ]

    table = Table(data, colWidths=[150, 250])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # 💰 PRICE (simple example)
    price = booking.room.price
    nights = (booking.check_out - booking.check_in).days
    total = price * nights

    elements.append(Paragraph(f"<b>Price per Night:</b> ₹{price}", styles['Normal']))
    elements.append(Paragraph(f"<b>Total Nights:</b> {nights}", styles['Normal']))
    elements.append(Paragraph(f"<b>Total Amount:</b> ₹{total}", styles['Heading2']))

    elements.append(Spacer(1, 40))

    # 📝 FOOTER
    elements.append(Paragraph("Thank you for booking with us!", styles['Italic']))

    doc.build(elements)

    return response

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
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})


# 🏠 HOME
def home(request):
    rooms = Room.objects.all()[:3]
    return render(request, 'booking/home.html', {'rooms': rooms})


# 🏨 ROOMS
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


# 📅 STEP 1
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

        if Booking.objects.filter(
            room=room,
            status='Booked',
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists():
            messages.error(request, "Already booked ❌")
            return redirect(request.path + f"?room_id={room_id}")

        request.session['check_in'] = str(check_in)
        request.session['check_out'] = str(check_out)

        return redirect(f"/book-details/?room_id={room_id}")

    return render(request, 'booking/select_date.html', {'room': room})


# 📅 STEP 2 (UPDATED)
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

        # 📞 PHONE
        country_code = request.POST.get('country_code')
        phone = request.POST.get('phone')
        phone = f"{country_code}{phone}"

        if not phone or not phone.replace("+", "").isdigit():
            messages.error(request, "Invalid phone number ❌")
            return redirect(request.path + f"?room_id={room_id}")

        # 🆔 AADHAR
        id_proof = request.POST.get('id_proof')
        if not id_proof or not id_proof.isdigit() or len(id_proof) != 12:
            messages.error(request, "Aadhar must be 12 digits ❌")
            return redirect(request.path + f"?room_id={room_id}")

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
            'id_proof': id_proof,
            'check_in': check_in,
            'check_out': check_out
        }

        return redirect('booking_summary')

    return render(request, 'booking/book_details.html', {
        'room': room,
        'people_range': people_range,
        'user': request.user
    })


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

        # 🔥 OTP generate
        otp = str(random.randint(100000, 999999))

        # DB me save
        OTP.objects.create(email=email, otp=otp)

        # 📩 Email send
        from django.core.mail import send_mail

        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True   # 🔥 MUST
            )
        except Exception as e:
            print("Email error:", e)

        # 🔐 session save
        request.session['email'] = email
        request.session['password'] = password

        messages.success(request, "OTP sent to your email 📩")
        return redirect('verify_otp')   # 👈 IMPORTANT

    return render(request, 'booking/signup.html')


def resend_otp(request):
    email = request.session.get('email')

    if not email:
        return redirect('signup')

    otp = str(random.randint(100000, 999999))

    OTP.objects.create(email=email, otp=otp)

    send_mail(
        'Resent OTP',
        f'Your new OTP is {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False
    )

    messages.success(request, "OTP resent 📩")
    return redirect('verify_otp')

# 🔐 LOGIN
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


# ❌ CANCEL BOOKING
@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.filter(id=booking_id, user=request.user).first()

    if not booking:
        messages.error(request, "Unauthorized ❌")
        return redirect('my_bookings')

    booking.status = 'Cancelled'
    booking.save()

    # 📩 EMAIL SEND (CANCEL)

    send_mail(
        'Booking Cancelled ❌',
        f'''
Hello {request.user.username},

Your booking has been cancelled ❌

Room: {booking.room.name}
Check-in: {booking.check_in}
Check-out: {booking.check_out}

If this was not you, contact support.
''',
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=False
    )

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

        # ================================
        # 🔒 DUPLICATE BOOKING PROTECTION (NEW ADD)
        # ================================
        if Booking.objects.filter(
            user=request.user,
            room=room,
            check_in=data['check_in'],
            check_out=data['check_out'],
            status='Booked'
        ).exists():
            messages.error(request, "Already booked ❌")
            return redirect('my_bookings')
        # ================================


        booking = Booking.objects.create(
            user=request.user,
            room=room,
            name=data['name'],
            phone=data['phone'],
            total_people=data['people'],
            id_proof=data['id_proof'],
            check_in=data['check_in'],
            check_out=data['check_out']
        )

        # 📩 NORMAL EMAIL (UNCHANGED)
        send_mail(
            'Booking Confirmed ✅',
            f'''
Hello {request.user.username},

Your booking is confirmed 🎉

Room: {room.name}
Check-in: {data['check_in']}
Check-out: {data['check_out']}
People: {data['people']}

Thank you for choosing us!
''',
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False
        )

        # ================================
        # 📄 PDF ATTACH EMAIL (UNCHANGED)
        # ================================
        from django.core.mail import EmailMessage
        from io import BytesIO

        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = []

        elements.append(Paragraph("HOTEL INVOICE", styles['Title']))
        elements.append(Spacer(1, 20))

        elements.append(Paragraph(f"Name: {booking.name}", styles['Normal']))
        elements.append(Paragraph(f"Phone: {booking.phone}", styles['Normal']))
        elements.append(Spacer(1, 20))

        data_table = [
            ["Room", booking.room.name],
            ["Check-in", str(booking.check_in)],
            ["Check-out", str(booking.check_out)],
            ["People", str(booking.total_people)],
        ]

        table = Table(data_table)
        elements.append(table)

        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        email = EmailMessage(
            'Booking Invoice 📄',
            'Your booking invoice is attached.',
            settings.EMAIL_HOST_USER,
            [request.user.email],
        )

        email.attach(
            f"invoice_{booking.id}.pdf",
            pdf,
            'application/pdf'
        )

        email.send(fail_silently=False)
        # ================================

        del request.session['booking_data']
        messages.success(request, "Booking confirmed 🎉")
        return redirect('my_bookings')

    return render(request, 'booking/booking_summary.html', {
        'room': room,
        'data': data
    })

# 🤖 CHATBOT (UNCHANGED)
def chatbot(request):
    msg = request.GET.get("message", "").lower()

    if not msg:
        return JsonResponse({"reply": "Hello..."})

    last_intent = request.session.get("last_intent")

    if "cheap" in msg or "best" in msg:
        room = Room.objects.order_by('price').first()

        if room:
            request.session["last_intent"] = "cheap"
            request.session["last_room"] = room.id
            return JsonResponse({"reply": f"{room.name} ₹{room.price}"})

        return JsonResponse({"reply": "No rooms"})

    elif "people" in msg:
        try:
            num = int(''.join(filter(str.isdigit, msg)))

            if last_intent == "cheap":
                room_id = request.session.get("last_room")
                room = Room.objects.get(id=room_id)

                if room.capacity >= num:
                    return JsonResponse({"reply": f"{room.name} is perfect for {num} people 👍"})
                else:
                    return JsonResponse({"reply": f"{room.name} is too small ❌ Try bigger room"})

            rooms = Room.objects.filter(capacity__gte=num)
            names = ", ".join([r.name for r in rooms])

            request.session["last_intent"] = "people"

            return JsonResponse({"reply": f"Rooms for {num} people: {names}"})

        except:
            return JsonResponse({"reply": "Try: 2 people"})

    elif "ac" in msg:
        rooms = Room.objects.filter(room_type="AC")
        names = ", ".join([r.name for r in rooms])

        request.session["last_intent"] = "ac"

        return JsonResponse({"reply": f"AC Rooms: {names}"})

    elif "under" in msg:
        try:
            price = int(''.join(filter(str.isdigit, msg)))
            rooms = Room.objects.filter(price__lte=price)
            names = ", ".join([f"{r.name} ₹{r.price}" for r in rooms])

            request.session["last_intent"] = "price"

            return JsonResponse({"reply": f"Rooms under ₹{price}: {names}"})

        except:
            return JsonResponse({"reply": "Try: under 3000"})

    elif "book" in msg and last_intent:
        return JsonResponse({
            "reply": "You can go to Rooms → select your last searched room → Book Now"
        })

    return JsonResponse({
        "reply": "Try: cheap room, AC, under 3000, 2 people"
    })