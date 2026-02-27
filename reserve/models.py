from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('hotel_owner', 'Hotel Owner'),
        ('customer', 'Customer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
class Hotel(models.Model):
    name      = models.CharField(max_length=255)
    location  = models.CharField(max_length=255, blank=True,null=True)
    address   = models.CharField(max_length=255, blank=True,null=True)
    phone     = models.CharField(max_length=50,  blank=True)
    website   = models.URLField(blank=True,null=True)
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available_rooms = models.PositiveIntegerField(blank=True, null=True)
    image     = models.ImageField(upload_to='media/hotels/', null=True, blank=True)  
    def __str__(self):
  
        return self.name
    
class Room(models.Model):
    hotel=models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number=models.CharField(max_length=10)
    room_type=models.CharField(max_length=50) #single double suite
    price=models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms=models.PositiveIntegerField()
    available_rooms=models.PositiveIntegerField()
    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number} ({self.room_type})"
    
class Guide(models.Model):
    name=models.CharField(max_length=255)
    location=models.CharField(max_length=255)
    phone=models.CharField(max_length=50)
    email=models.EmailField()
    description=models.TextField(blank=True)
    price_per_day=models.DecimalField(max_digits=10, decimal_places=2)
    image=models.ImageField(upload_to='media/guides/', null=True, blank=True)
    is_available=models.BooleanField(default=True)
    specialization=models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.SET_NULL, null=True, blank=True)
    check_in = models.DateField()
    check_out = models.DateField()
    num_rooms = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.user.username}"
    
class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.hotel.name}"
    
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    image=models.ImageField(upload_to='media/customers/', null=True, blank=True)

    
    def __str__(self):
        return self.user.username
    
class HotelOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    image=models.ImageField(upload_to='media/hotel_owners/', null=True, blank=True)

    
    def __str__(self):
        return self.user.username
    