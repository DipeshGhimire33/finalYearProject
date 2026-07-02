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
admin.site.register(Destination)
admin.site.register(DestinationMustVisit)
admin.site.register(DestinationPopular)
admin.site.register(AppReview)
admin.site.register(HotelReview)
admin.site.register(DestinationExperience)
admin.site.register(ContactMessage)
# admin.site.register(Payment)
# admin.site.register(Cancellation)

# admin.site.register(Refund)
