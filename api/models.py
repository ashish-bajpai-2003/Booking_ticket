from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

# Custom user model
class CustomUser(AbstractUser):
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.username

import random
import string

def generate_pnr():
    return ''.join(random.choices(string.digits, k=8))

def get_current_date():
    return timezone.now().date()

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('waiting', 'Waiting'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    seat_number = models.CharField(max_length=10, null=True, blank=True)
    booked_at = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    seat_class = models.CharField(max_length=20)
    number_of_seats= models.PositiveIntegerField()
    train_number = models.CharField(max_length=20)
    departure_date = models.DateField(default=get_current_date) 
    # departure_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(default="14:30:00")
    # origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    pnr_number = models.CharField(max_length=8, default=generate_pnr, db_index=True)
    name = models.CharField(max_length=100) 


    #  JSON.LOAD PAYLOAD

    def __str__(self):
        return f"PNR: {self.pnr_number} | Seat: {self.seat_number or 'Waiting'} | Status: {self.status}"
    


class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField(default="14:30:00")
    arrival_time = models.TimeField(default="14:30:00")
    departure_date = models.DateField()
    total_seats = models.PositiveIntegerField(default=100)

    # ✅ Replaced deprecated import
    seat_info = models.JSONField(default=dict)

    booked_seats = models.IntegerField(default=0)
    available_seats = models.IntegerField(default=100)

    from django.contrib.postgres.fields import ArrayField  # You can keep this
    seat_info_array = ArrayField(
        models.CharField(max_length=20),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.train_name} ({self.train_number})"
    

class Stoppage(models.Model):
    train = models.ForeignKey(Train, related_name='stoppages', on_delete=models.CASCADE)
    station_name = models.CharField(max_length=100)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    order = models.IntegerField()

    def __str__(self):
        return f"{self.train.train_number} - {self.station_name}"
