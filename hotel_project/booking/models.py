
from django.db import models

class Room(models.Model):
    ROOM_TYPES = (
        ('AC', 'AC'),
        ('NON-AC', 'Non-AC'),
        ('DELUXE', 'Deluxe'),
    )

    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price = models.IntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    name = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return self.name