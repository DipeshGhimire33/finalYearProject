from django.contrib import admin
from django.urls import path
from .models import Destination, Guide ,Hotel,GuideAvailability,Customer, Booking, Review, Payment,Cancellation,Itinerary,Refund
#add hotel
# Register your models here.
admin.site.register(Destination)
admin.site.register(Guide)
admin.site.register(GuideAvailability)
admin.site.register(Hotel)
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Cancellation)
admin.site.register(Itinerary)
admin.site.register(Refund)
