
from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    # Main map view
    path('', views.MapView.as_view(), name='map_view'),
    path('api/locations/', views.get_all_locations, name='get_all_locations'),
    path('api/calculate-path/', views.calculate_shortest_path, name='calculate_shortest_path'),
    path('api/nearby/', views.get_nearby_locations, name='get_nearby_locations'),
    path('api/route/<int:route_id>/', views.get_route_details, name='get_route_details'),
]