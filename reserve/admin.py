from django.contrib import admin
from django.urls import path
from .models import Guide ,Hotel,Booking
#Review, Payment,Cancellation,Itinerary,Refund

# Register your models here.

admin.site.register(Guide)
admin.site.register(Hotel)
admin.site.register(Booking)
# admin.site.register(Review)
# admin.site.register(Payment)
# admin.site.register(Cancellation)

# admin.site.register(Refund)
