from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# =====================================================
# User Profile 
# =====================================================
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('hotel_owner', 'Hotel Owner'),
        ('customer', 'Customer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


#to get hotels from the api and save to database

class Hotel(models.Model):
    name      = models.CharField(max_length=255)
    location  = models.CharField(max_length=255, blank=True,null=True)
    address   = models.CharField(max_length=255, blank=True,null=True)
    phone     = models.CharField(max_length=50,  blank=True)
    website   = models.URLField(blank=True)
    lat       = models.FloatField(null=True, blank=True)
    lng       = models.FloatField(null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)  
    def __str__(self):
  
        return self.name
    


    #old models 
# =====================================================
# DESTINATION
# =====================================================
class Destination(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField()
    best_season = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =====================================================
# GUIDE
# =====================================================
class Guide(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='guides/')
    languages = models.CharField(max_length=200)  # English, Nepali, Hindi
    experience_years = models.PositiveIntegerField()
    license_number = models.CharField(max_length=50, unique=True)
    fee_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# =====================================================
# GUIDE AVAILABILITY
# =====================================================
class GuideAvailability(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='availability')
    available_from = models.DateField()
    available_to = models.DateField()

    def __str__(self):
        return f"{self.guide} availability"







# =====================================================
# CUSTOMER / TOURIST
# =====================================================
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    nationality = models.CharField(max_length=50)
    passport_number = models.CharField(max_length=50, unique=True)
    emergency_contact = models.CharField(max_length=100)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# =====================================================
# TOUR PACKAGE
# =====================================================
class TourPackage(models.Model):
    title = models.CharField(max_length=150)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    duration_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_people = models.PositiveIntegerField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# =====================================================
# ITINERARY
# =====================================================
class Itinerary(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='itinerary')
    day_number = models.PositiveIntegerField()
    activity = models.TextField()

    def __str__(self):
        return f"{self.package} - Day {self.day_number}"


# =====================================================
# BOOKING
# =====================================================
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.SET_NULL, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True)
    travel_date = models.DateField()
    number_of_people = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id}"


# =====================================================
# PAYMENT
# =====================================================
class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    is_successful = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking #{self.booking.id}"


# =====================================================
# CANCELLATION
# =====================================================
class Cancellation(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    reason = models.TextField()
    cancelled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancellation for Booking #{self.booking.id}"


# =====================================================
# REFUND
# =====================================================
class Refund(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    refunded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund for Booking #{self.booking.id}"


# =====================================================
# REVIEW
# =====================================================
class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer}"
