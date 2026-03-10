
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Location(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude coordinate (-90 to 90)"
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude coordinate (-180 to 180)"
    )
    address = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class TouristAttraction(Location): #exetnds the model Location to include specific fields for tourist attractions
    CATEGORY_CHOICES = [
        ('historical', 'Historical Site'),
        ('natural', 'Natural Wonder'),
        ('museum', 'Museum'),
        ('religious', 'Religious Site'),
        ('entertainment', 'Entertainment'),
        ('adventure', 'Adventure Activity'),
        ('cultural', 'Cultural Site'),
        ('beach', 'Beach'),
        ('park', 'Park/Garden'),
        ('viewpoint', 'Viewpoint'),
        ('other', 'Other'),
    ]
    
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='other'
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rating out of 5.0"
    )
    entry_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Entry fee in local currency"
    )
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    image = models.ImageField(
        upload_to='attractions/', 
        blank=True, 
        null=True,
        help_text="Upload an image of the attraction"
    )
    
    class Meta:
        verbose_name = "Tourist Attraction"
        verbose_name_plural = "Tourist Attractions"


class EVChargingStation(Location):
    """
    Model for Electric Vehicle charging stations.
    Includes charger specifications, availability, and operator information.
    """
    CHARGER_TYPE_CHOICES = [
        ('type1', 'Type 1 (J1772)'),
        ('type2', 'Type 2 (Mennekes)'),
        ('ccs', 'CCS (Combined Charging System)'),
        ('chademo', 'CHAdeMO'),
        ('tesla', 'Tesla Supercharger'),
        ('universal', 'Universal'),
    ]
    
    POWER_LEVEL_CHOICES = [
        ('level1', 'Level 1 (120V)'),
        ('level2', 'Level 2 (240V)'),
        ('dcfast', 'DC Fast Charging'),
    ]
    
    charger_type = models.CharField(
        max_length=20, 
        choices=CHARGER_TYPE_CHOICES
    )
    power_level = models.CharField(
        max_length=20, 
        choices=POWER_LEVEL_CHOICES
    )
    number_of_ports = models.PositiveIntegerField(
        default=1,
        help_text="Number of available charging ports"
    )
    charging_speed = models.CharField(
        max_length=50, 
        help_text="e.g., '50 kW' or '150 kW'"
    )
    is_operational = models.BooleanField(
        default=True,
        help_text="Is this charging station currently operational?"
    )
    cost_per_kwh = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Cost per kilowatt-hour"
    )
    operator = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Company or organization operating this station"
    )
    contact_number = models.CharField(max_length=20, blank=True)
    available_24_7 = models.BooleanField(
        default=False,
        help_text="Is this station available 24 hours a day?"
    )
    requires_membership = models.BooleanField(
        default=False,
        help_text="Does this station require membership to use?"
    )
    
    class Meta:
        verbose_name = "EV Charging Station"
        verbose_name_plural = "EV Charging Stations"


class Route(models.Model):
    """
    Model to store calculated routes between locations.
    Stores the complete path with distance and time metrics.
    """
    name = models.CharField(max_length=200)
    start_point = models.CharField(max_length=200)
    end_point = models.CharField(max_length=200)
    start_lat = models.FloatField()
    start_lng = models.FloatField()
    end_lat = models.FloatField()
    end_lng = models.FloatField()
    total_distance = models.FloatField(
        help_text="Total distance in kilometers"
    )
    estimated_time = models.FloatField(
        help_text="Estimated travel time in minutes", 
        null=True, 
        blank=True
    )
    path_coordinates = models.JSONField(
        help_text="List of waypoints with latitude/longitude coordinates",
        default=list
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Username or identifier of who created this route"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name}: {self.start_point} to {self.end_point}"


class Waypoint(models.Model):
    """
    Model for intermediate points/stops in a route.
    Each waypoint belongs to a specific route and has an order.
    """
    route = models.ForeignKey(
        Route, 
        on_delete=models.CASCADE, 
        related_name='waypoints'
    )
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    order = models.PositiveIntegerField(
        help_text="Order of this waypoint in the route (1, 2, 3, ...)"
    )
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} (Stop {self.order})"
