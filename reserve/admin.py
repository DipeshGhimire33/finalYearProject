from django.contrib import admin
from django.urls import path
from .models import *
#Review, Payment,Cancellation,Itinerary,Refund

# Register your models here.

admin.site.register(Guide)
admin.site.register(Hotel)
admin.site.register(Booking)
admin.site.register(Room)
admin.site.register(Package)
admin.site.register(Trip)
admin.site.register(UserProfile)
admin.site.register(Equipment)
admin.site.register(BookingEquipment)
admin.site.register(Vehicle)
admin.site.register(HotelBooking)
# admin.site.register(Review)
# admin.site.register(Payment)
# admin.site.register(Cancellation)

# admin.site.register(Refund)
