from django.contrib import admin

# Register your models here.
# tourism_maps/admin.py
# Django admin configuration for managing tourist attractions, EV stations, and routes

from django.contrib import admin
from .models import TouristAttraction, EVChargingStation, Route, Waypoint


@admin.register(TouristAttraction)
class TouristAttractionAdmin(admin.ModelAdmin):
    """Admin interface for managing tourist attractions."""
    list_display = ['name', 'category', 'rating', 'entry_fee', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'address']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'rating', 'image')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Details', {
            'fields': ('entry_fee', 'opening_time', 'closing_time', 'contact_number', 'website')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(EVChargingStation)
class EVChargingStationAdmin(admin.ModelAdmin):
    """Admin interface for managing EV charging stations."""
    list_display = ['name', 'charger_type', 'power_level', 'number_of_ports', 
                    'is_operational', 'is_active', 'created_at']
    list_filter = ['charger_type', 'power_level', 'is_operational', 'is_active']
    search_fields = ['name', 'description', 'address', 'operator']
    list_editable = ['is_operational', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'operator')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Charger Details', {
            'fields': ('charger_type', 'power_level', 'number_of_ports', 
                      'charging_speed', 'cost_per_kwh')
        }),
        ('Availability', {
            'fields': ('is_operational', 'available_24_7', 'requires_membership', 
                      'contact_number')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


class WaypointInline(admin.TabularInline):
    """Inline admin for waypoints."""
    model = Waypoint
    extra = 0
    fields = ['name', 'latitude', 'longitude', 'order']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    """Admin interface for saved routes."""
    list_display = ['name', 'start_point', 'end_point', 'total_distance', 
                    'estimated_time', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'start_point', 'end_point', 'created_by']
    readonly_fields = ['created_at']
    inlines = [WaypointInline]
    
    fieldsets = (
        ('Route Information', {
            'fields': ('name', 'created_by')
        }),
        ('Start Point', {
            'fields': ('start_point', 'start_lat', 'start_lng')
        }),
        ('End Point', {
            'fields': ('end_point', 'end_lat', 'end_lng')
        }),
        ('Route Metrics', {
            'fields': ('total_distance', 'estimated_time', 'path_coordinates')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

