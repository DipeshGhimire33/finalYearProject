from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from .models import TouristAttraction, EVChargingStation, Route, Waypoint
import json
import math
import heapq
from typing import List, Dict, Tuple


class MapView(TemplateView):
    """
    Main map view that displays the interactive map interface.
    Shows all active tourist attractions and EV charging stations.
    """
    template_name = 'maps.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tourist_attractions'] = TouristAttraction.objects.filter(is_active=True)
        context['ev_stations'] = EVChargingStation.objects.filter(is_active=True)
        return context


def get_all_locations(request):
    """
    API endpoint to retrieve all active locations as JSON.
    Returns tourist attractions and EV charging stations separately.
    
    Returns:
        JsonResponse with 'tourist_attractions' and 'ev_stations' arrays
    """
    tourist_attractions = TouristAttraction.objects.filter(is_active=True).values(
        'id', 'name', 'latitude', 'longitude', 'category', 'rating', 
        'entry_fee', 'description', 'address'
    )
    
    ev_stations = EVChargingStation.objects.filter(is_active=True).values(
        'id', 'name', 'latitude', 'longitude', 'charger_type', 'power_level',
        'number_of_ports', 'charging_speed', 'is_operational', 'description', 'address'
    )
    
    data = {
        'tourist_attractions': list(tourist_attractions),
        'ev_stations': list(ev_stations),
    }
    
    return JsonResponse(data)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    Uses the Haversine formula for accurate geographic distance calculation.
    
    Args:
        lat1: Latitude of first point (in decimal degrees)
        lon1: Longitude of first point (in decimal degrees)
        lat2: Latitude of second point (in decimal degrees)
        lon2: Longitude of second point (in decimal degrees)
    
    Returns:
        Distance in kilometers
    
    Formula:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        c = 2 * arcsin(√a)
        distance = Earth_radius * c
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers (mean radius)
    r = 6371
    
    return c * r


def build_graph(locations: List[Dict]) -> Dict[int, Dict[int, float]]:
    """
    Build a weighted graph from a list of locations.
    Each location is connected to all other locations with edge weights
    representing the distance between them.
    
    Args:
        locations: List of dictionaries with 'latitude' and 'longitude' keys
    
    Returns:
        Adjacency dictionary: {node_index: {neighbor_index: distance}}
    
    Example:
        locations = [
            {'latitude': 27.7, 'longitude': 85.3, 'name': 'A'},
            {'latitude': 28.2, 'longitude': 83.9, 'name': 'B'}
        ]
        graph = build_graph(locations)
        # graph = {0: {1: 123.45}, 1: {0: 123.45}}
    """
    graph = {}
    
    for i, loc1 in enumerate(locations):
        graph[i] = {}
        for j, loc2 in enumerate(locations):
            if i != j:
                distance = haversine_distance(
                    loc1['latitude'], loc1['longitude'],
                    loc2['latitude'], loc2['longitude']
                )
                graph[i][j] = distance
    
    return graph


def dijkstra(graph: Dict[int, Dict[int, float]], start: int, end: int) -> Tuple[List[int], float]:
    """
    DIJKSTRA'S SHORTEST PATH ALGORITHM
    
    Finds the shortest path between two nodes in a weighted graph.
    This is the core algorithm for route calculation.
    
    Algorithm Steps:
    1. Initialize all distances to infinity except start node (0)
    2. Use a priority queue to always process the nearest unvisited node
    3. For each node, update distances to neighbors if a shorter path is found
    4. Track the previous node for each to reconstruct the final path
    5. Stop when the destination is reached
    6. Backtrack from destination to start to get the complete path
    
    Args:
        graph: Adjacency dictionary {node: {neighbor: distance}}
        start: Starting node index
        end: Ending node index
    
    Returns:
        Tuple of (path as list of node indices, total distance in km)
    
    Time Complexity: O((V + E) log V) where V = vertices, E = edges
    Space Complexity: O(V)
    
    Example:
        graph = {0: {1: 10, 2: 5}, 1: {2: 2}, 2: {1: 3}}
        path, distance = dijkstra(graph, 0, 1)
        # path = [0, 2, 1], distance = 8
    """
    # Initialize distances: all nodes start at infinity except start node
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    
    # Track previous node in optimal path for path reconstruction
    previous = {node: None for node in graph}
    
    # Priority queue: stores (distance, node) tuples
    # heapq ensures we always process the nearest unvisited node
    pq = [(0, start)]
    visited = set()
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # Skip if already visited (can happen with duplicate entries)
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        # If we reached the destination, reconstruct and return the path
        if current_node == end:
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = previous[node]
            path.reverse()
            return path, distances[end]
        
        # Check all neighbors of the current node
        if current_node in graph:
            for neighbor, weight in graph[current_node].items():
                distance = current_distance + weight
                
                # If we found a shorter path to neighbor, update it
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
    
    # No path found between start and end
    return [], float('infinity')


@csrf_exempt
def calculate_shortest_path(request):
    """
    Main API endpoint for calculating the shortest path between two points.
    Uses Dijkstra's algorithm to find the optimal route.
    
    Expects POST request with JSON body:
    {
        "start_lat": 28.3949,
        "start_lng": 84.1240,
        "end_lat": 27.7172,
        "end_lng": 85.3240,
        "include_waypoints": [1, 3, 5],  // Optional: IDs of locations to include
        "save_route": false,              // Optional: whether to save this route
        "route_name": "My Trip"           // Optional: name for saved route
    }
    
    Returns JSON:
    {
        "success": true,
        "path": [...],                    // Array of locations in order
        "total_distance": 123.45,         // Total distance in km
        "estimated_time": 147.4,          // Estimated time in minutes
        "segments": [...],                // Distance breakdown by segment
        "number_of_stops": 4,             // Total number of stops
        "route_id": 123                   // ID of saved route (if save_route=true)
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        data = json.loads(request.body)
        start_lat = float(data.get('start_lat'))
        start_lng = float(data.get('start_lng'))
        end_lat = float(data.get('end_lat'))
        end_lng = float(data.get('end_lng'))
        include_waypoints = data.get('include_waypoints', [])  # List of location IDs
        
        # Build list of all locations: start + waypoints + end
        locations = [
            {
                'latitude': start_lat, 
                'longitude': start_lng, 
                'name': 'Start', 
                'type': 'start'
            }
        ]
        
        # Add tourist attractions and EV stations as potential waypoints
        if include_waypoints:
            for loc_id in include_waypoints:
                # Try to find in tourist attractions first
                try:
                    attraction = TouristAttraction.objects.get(id=loc_id, is_active=True)
                    locations.append({
                        'latitude': attraction.latitude,
                        'longitude': attraction.longitude,
                        'name': attraction.name,
                        'type': 'attraction',
                        'id': attraction.id
                    })
                except TouristAttraction.DoesNotExist:
                    # If not found, try EV charging stations
                    try:
                        station = EVChargingStation.objects.get(id=loc_id, is_active=True)
                        locations.append({
                            'latitude': station.latitude,
                            'longitude': station.longitude,
                            'name': station.name,
                            'type': 'ev_station',
                            'id': station.id
                        })
                    except EVChargingStation.DoesNotExist:
                        # Location not found, skip it
                        pass
        
        # Add end point
        locations.append({
            'latitude': end_lat, 
            'longitude': end_lng, 
            'name': 'End', 
            'type': 'end'
        })
        
        # Build graph with all locations
        graph = build_graph(locations)
        
        # Run Dijkstra's algorithm
        start_idx = 0
        end_idx = len(locations) - 1
        path_indices, total_distance = dijkstra(graph, start_idx, end_idx)
        
        if not path_indices:
            return JsonResponse({'error': 'No path found'}, status=404)
        
        # Build path with full location details
        path = []
        for idx in path_indices:
            loc = locations[idx]
            path.append({
                'name': loc['name'],
                'latitude': loc['latitude'],
                'longitude': loc['longitude'],
                'type': loc.get('type', 'waypoint'),
                'id': loc.get('id')
            })
        
        # Calculate distance for each segment of the path
        segments = []
        for i in range(len(path) - 1):
            segment_distance = haversine_distance(
                path[i]['latitude'], path[i]['longitude'],
                path[i+1]['latitude'], path[i+1]['longitude']
            )
            segments.append({
                'from': path[i]['name'],
                'to': path[i+1]['name'],
                'distance': round(segment_distance, 2)
            })
        
        # Estimate travel time (assuming average speed of 50 km/h)
        estimated_time = (total_distance / 50) * 60  # Convert to minutes
        
        response_data = {
            'success': True,
            'path': path,
            'total_distance': round(total_distance, 2),
            'estimated_time': round(estimated_time, 2),
            'segments': segments,
            'number_of_stops': len(path)
        }
        
        # Optionally save the route to database
        if data.get('save_route'):
            route = Route.objects.create(
                name=data.get('route_name', f"Route from {path[0]['name']} to {path[-1]['name']}"),
                start_point=path[0]['name'],
                end_point=path[-1]['name'],
                start_lat=start_lat,
                start_lng=start_lng,
                end_lat=end_lat,
                end_lng=end_lng,
                total_distance=total_distance,
                estimated_time=estimated_time,
                path_coordinates=path
            )
            response_data['route_id'] = route.id
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_nearby_locations(request):
    """
    Find tourist attractions and EV stations within a specified radius.
    
    Expects GET parameters:
        lat: Latitude of center point
        lng: Longitude of center point
        radius: Search radius in kilometers (default: 10 km)
    
    Example:
        /maps/api/nearby/?lat=28.3949&lng=84.1240&radius=5
    
    Returns JSON:
    {
        "attractions": [...],         // Nearby tourist attractions
        "ev_stations": [...],         // Nearby EV charging stations
        "search_center": {...},       // Center point coordinates
        "radius": 10                  // Search radius used
    }
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        radius = float(request.GET.get('radius', 10))  # Default 10 km
        
        nearby_attractions = []
        nearby_stations = []
        
        # Find nearby tourist attractions
        for attraction in TouristAttraction.objects.filter(is_active=True):
            distance = haversine_distance(lat, lng, attraction.latitude, attraction.longitude)
            if distance <= radius:
                nearby_attractions.append({
                    'id': attraction.id,
                    'name': attraction.name,
                    'latitude': attraction.latitude,
                    'longitude': attraction.longitude,
                    'category': attraction.category,
                    'rating': float(attraction.rating) if attraction.rating else None,
                    'distance': round(distance, 2),
                    'description': attraction.description
                })
        
        # Find nearby EV charging stations
        for station in EVChargingStation.objects.filter(is_active=True):
            distance = haversine_distance(lat, lng, station.latitude, station.longitude)
            if distance <= radius:
                nearby_stations.append({
                    'id': station.id,
                    'name': station.name,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                    'charger_type': station.charger_type,
                    'power_level': station.power_level,
                    'is_operational': station.is_operational,
                    'distance': round(distance, 2),
                    'description': station.description
                })
        
        # Sort by distance (nearest first)
        nearby_attractions.sort(key=lambda x: x['distance'])
        nearby_stations.sort(key=lambda x: x['distance'])
        
        return JsonResponse({
            'attractions': nearby_attractions,
            'ev_stations': nearby_stations,
            'search_center': {'lat': lat, 'lng': lng},
            'radius': radius
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_route_details(request, route_id):
    """
    Retrieve details of a previously saved route.
    
    Args:
        route_id: ID of the route to retrieve
    
    Returns JSON with route details:
    {
        "id": 123,
        "name": "My Trip",
        "start_point": "Start",
        "end_point": "End",
        "total_distance": 123.45,
        "estimated_time": 147.4,
        "path": [...],
        "created_at": "2024-01-15T10:30:00"
    }
    """
    route = get_object_or_404(Route, id=route_id)
    
    data = {
        'id': route.id,
        'name': route.name,
        'start_point': route.start_point,
        'end_point': route.end_point,
        'total_distance': route.total_distance,
        'estimated_time': route.estimated_time,
        'path': route.path_coordinates,
        'created_at': route.created_at.isoformat()
    }
    
    return JsonResponse(data)

# Create your views here.
