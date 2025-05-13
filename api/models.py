from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

# Custom user model
class CustomUser(AbstractUser):
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.username
def get_current_datetime():
    return timezone.now() 
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
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    seat_number = models.CharField(max_length=10, null=True, blank=True)
    booked_at = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    seat_class = models.CharField(max_length=20)
    fare = models.FloatField()
    number_of_seats = models.PositiveIntegerField()
    train_number = models.CharField(max_length=20)
    departure_date = models.DateField()
    # departure_datetime = models.DateTimeField(default=get_current_datetime)  # Combined date and time
    destination = models.CharField(max_length=100)
    pnr_number = models.CharField(max_length=8, default=generate_pnr, db_index=True, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"PNR: {self.pnr_number} | Seat: {self.seat_number or 'Waiting'} | Status: {self.status}"

def default_running_days():
    # If the train is daily, return all days
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField(default="14:30:00")
    arrival_time = models.TimeField(default="14:30:00")
    total_seats = models.PositiveIntegerField(default=100)
    train_creation_date = models.DateField(default=get_current_date) 
    distance = models.IntegerField() 
    


    # ✅ Replaced deprecated import
    seat_info = models.JSONField(default=dict)

    booked_seats = models.IntegerField(default=0)
    available_seats = models.IntegerField(default=100)
    stoppages = models.JSONField(default=list)

    from django.contrib.postgres.fields import ArrayField  # You can keep this
    seat_info_array = ArrayField(
        models.CharField(max_length=20),
        blank=True,
        null=True
    )
     # Running days of the train
    running_days = ArrayField(
        models.CharField(max_length=10, choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday"),
        ]),
        blank=True,
        null=True,
        default=default_running_days,
        help_text="Select the days on which the train runs",
    )




    train_type = models.CharField(max_length=50)  # e.g., Express, Superfast, Vande Bharat
    distance_in_km = models.PositiveIntegerField()
    base_fare_per_km = models.FloatField() 

    def __str__(self):
        return f"{self.train_name} ({self.train_number})"
    

