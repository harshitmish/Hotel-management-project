from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    ROOM_TYPES = (
        ('AC', 'AC'),
        ('NON-AC', 'Non-AC'),
        ('DELUXE', 'Deluxe'),
    )

    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price = models.IntegerField()

    description = models.TextField(blank=True, null=True)
    features = models.TextField(blank=True, null=True)

    capacity = models.IntegerField(default=2)
    
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)

    def __str__(self):
        return self.name


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')

    def __str__(self):
        return self.room.name


from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Booked', 'Booked'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    total_people = models.IntegerField(null=True, blank=True)
    id_proof = models.CharField(max_length=100, null=True, blank=True)

    check_in = models.DateField()
    check_out = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Booked')  # ✅ NEW

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.room.name} ({self.check_in} to {self.check_out}) - {self.status}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')  # 🔥 FIX

    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.room.name} ({self.rating})"