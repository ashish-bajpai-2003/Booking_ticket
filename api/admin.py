from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Booking

# Custom UserAdmin to display the 'is_owner' field
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_owner', 'is_staff', 'is_active']  # Display these fields in the admin list

    # Add the 'is_owner' field to the 'User Creation' and 'User Change' forms
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_owner',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_owner',)}),
    )

# Register the CustomUser model with the customized UserAdmin
admin.site.register(CustomUser, CustomUserAdmin)






@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event_name', 'seats_booked', 'booking_date', 'status')
