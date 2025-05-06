from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Custom user model
class CustomUser(AbstractUser):
    # Additional field to differentiate between owner and normal user
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.username





class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=255)
    seats_booked = models.PositiveIntegerField()
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Booked', 'Booked'), ('Cancelled', 'Cancelled')], default='Booked')

    def __str__(self):
        return f"{self.user.username} - {self.event_name} ({self.status})"