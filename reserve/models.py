from django.db import models 
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.conf import settings


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("hotel_owner", "Hotel Owner"),
        ("customer", "Customer"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

class Destination(models.Model):
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='media/destinations/', null=True, blank=True)

    def __str__(self):
        return self.name

class DestinationPopular(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='popular_places')
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='media/destination/popular/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.destination.name}"

class DestinationMustVisit(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='must_visit_places')
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='media/destination/must_visit/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.destination.name}"
class Hotel(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hotels",
        null=True,      # keep null=True since you already have existing data
        blank=True
    )

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available_rooms = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='media/hotels/', blank=True, null=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel           = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number     = models.CharField(max_length=10)
    room_type       = models.CharField(max_length=50)   # single / double / suite
    price           = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms     = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number} ({self.room_type})"

class Guide(models.Model):
    name            = models.CharField(max_length=255)
    location        = models.CharField(max_length=255)
    phone           = models.CharField(max_length=50)
    email           = models.EmailField()
    description     = models.TextField(blank=True)
    price_per_day   = models.DecimalField(max_digits=10, decimal_places=2)   # FIX: was referenced as guide.price in views
    image           = models.ImageField(upload_to='media/guides/', null=True, blank=True)
    is_available    = models.BooleanField(default=True)
    specialization  = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class HotelBooking(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )

    guide = models.ForeignKey(
        Guide,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    check_in = models.DateField()

    check_out = models.DateField()

    num_rooms = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return f"{self.hotel.name} booking {self.id}"
    

class Equipment(models.Model):
    CATEGORY_CHOICES = (
        ('camera', 'Camera'),
        ('camping', 'Camping'),
        ('clothing', 'Clothing'),
        ('hiking', 'Hiking'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Trip(models.Model):
    # FIX: user is nullable so unauthenticated users don't crash the ForeignKey
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    fullname        = models.CharField(max_length=255, blank=True)
    email           = models.EmailField(blank=True)

    pickup          = models.CharField(max_length=255)
    destination     = models.CharField(max_length=255)

    pickup_lat      = models.FloatField(null=True, blank=True)
    pickup_lng      = models.FloatField(null=True, blank=True)

    destination_lat = models.FloatField(null=True, blank=True)
    destination_lng = models.FloatField(null=True, blank=True)

    people          = models.IntegerField(default=1)
    days            = models.IntegerField(default=1)

    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pickup} → {self.destination}"    
class Booking(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )

    guide = models.ForeignKey(
        Guide,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


    check_in = models.DateField()

    check_out = models.DateField()


    num_rooms = models.PositiveIntegerField(
        default=1
    )


    people = models.PositiveIntegerField(
        default=1
    )


    distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    vehicle_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    payment_status = models.BooleanField(
        default=False
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return f"Booking #{self.id} - {self.user.username}"
class BookingEquipment(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="equipment_items"
    )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.booking.id} - {self.equipment.name}"
    
class Vehicle(models.Model):

    name = models.CharField(max_length=100)

    capacity = models.PositiveIntegerField(
        default=15
    )

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='vehicles/',
        blank=True,
        null=True
    )

    available = models.BooleanField(default=True)


    def __str__(self):
        return self.name

class Package(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="package",
         null=True,
    blank=True,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    days = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    

class AppReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class HotelReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class DestinationExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="gallery/")
    caption = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.destination.name}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Customer(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone   = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    image   = models.ImageField(upload_to='media/customers/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class HotelOwner(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    phone   = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    image   = models.ImageField(upload_to='media/hotel_owners/', null=True, blank=True)

    def __str__(self):
        return self.user.username

from django.shortcuts import redirect


