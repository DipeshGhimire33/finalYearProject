# Create your views here.
import os
from dotenv import load_dotenv
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomerRegistrationForm
from .models import Hotel, UserProfile
import requests
from django.shortcuts import render

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  # ✅ safe way to load API key from .env file


def index(request):
    return render(request, 'index.html')
def base(request):
    return render(request, 'base.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            # user.username = form.cleaned_data['email']  # Use email as username
            user.set_password(form.cleaned_data['password1'])
            user.save()

            # ✅ Get the role the user selected from the form
            role = form.cleaned_data['role']
            UserProfile.objects.create(user=user, role=role)

            login(request, user)

            # ✅ Redirect based on role
            if role == 'hotel_owner':
                return redirect('dashboard')
            else:
                return redirect('index')
        else:
            messages.error(request, "Please fix the errors below.")

    else:
        form = CustomerRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def get_photo_url(photo_reference):
    if photo_reference:
        return (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth=800"
            f"&photoreference={photo_reference}"
            f"&key={GOOGLE_API_KEY}"
        )
    return None


# def hotelsAPI(request):
    
    
#     if request.method == "POST":
#         city = request.POST.get('city', '').strip()
#     if request.method == "POST":
#         city = request.POST.get('city', '').strip()
        
#         if not city:
#             messages.error(request, "Please enter a city name!")
#             return render(request, 'hotels_api.html', {'hotels': Hotel.objects.all()})
        
#         try:
#             # Step 1: Get city coordinates
#             geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_API_KEY}"
#             geo_response = requests.get(geocode_url).json()
            
#             if not geo_response.get('results'):
#                 messages.error(request, f"City '{city}' not found.")
#                 return render(request, 'hotels_api.html', {'hotels': Hotel.objects.all()})
            
#             location = geo_response['results'][0]['geometry']['location']
#             lat, lng = location['lat'], location['lng']
            
#             # Step 2: Search for hotels
#             places_url = (
#                 f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
#                 f"?location={lat},{lng}"
#                 f"&radius=5000"
#                 f"&type=lodging"
#                 f"&key={GOOGLE_API_KEY}"
#             )
#             places_response = requests.get(places_url).json()
#             results = places_response.get('results', [])
            
#             if not results:
#                 messages.warning(request, f"No hotels found in {city}.")
            
#             # Step 3: Save hotels to database
#             for result in results:
#                 photos = result.get('photos', [])
#                 photo_ref = photos[0].get('photo_reference') if photos else None
#                 image_url = get_photo_url(photo_ref)
                
#                 name = result.get('name', 'Unknown Hotel')
#                 address = result.get('vicinity', 'N/A')
#                 hotel_lat = result['geometry']['location']['lat']
#                 hotel_lng = result['geometry']['location']['lng']
                
#                 Hotel.objects.get_or_create(
#                     name=name,
#                     defaults={
#                         'location': city,
#                         'address': address,
#                         'lat': hotel_lat,
#                         'lng': hotel_lng,
#                         'image_url': image_url,
#                     }
#                 )
            
#             messages.success(request, f"Loaded {len(results)} hotels in {city}!")
            
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
    
#     hotels = Hotel.objects.all()
#     return render(request, 'hotels_api.html', {'hotels': hotels})


def hotelsAPI(request):
    if request.method == "POST":
        city = request.POST.get('city', '').strip()
        
        if not city:
            messages.error(request, "Please enter a city name!")
            return render(request, 'hotels_api.html', {'hotels': Hotel.objects.all()})
        
        try:
            # Step 1: Get city coordinates
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_API_KEY}"
            
            print(f"🔍 Searching for: {city}")
            print(f"📡 Request URL: {geocode_url}")
            
            geo_response = requests.get(geocode_url).json()
            
            print(f"📦 Full API Response:")
            print(geo_response)  # ✅ This will show us EVERYTHING
            print(f"📊 Status: {geo_response.get('status')}")
            
            # Check for API errors
            if geo_response.get('status') == 'REQUEST_DENIED':
                error_msg = geo_response.get('error_message', 'API access denied')
                messages.error(request, f"API Error: {error_msg}")
                print(f"❌ REQUEST DENIED: {error_msg}")
                return render(request, 'hotels_api.html', {'hotels': Hotel.objects.all()})
            
            if not geo_response.get('results'):
                messages.error(request, f"City '{city}' not found.")
                print(f"❌ No results for {city}")
                return render(request, 'hotels_api.html', {'hotels': Hotel.objects.all()})
            
            location = geo_response['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            print(f"✅ Found coordinates: {lat}, {lng}")
            
            # ... rest of your code
            
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            print(f"❌ Exception: {str(e)}")
            import traceback
            traceback.print_exc()  # ✅ Print full error trace
    
    hotels = Hotel.objects.all()
    return render(request, 'hotels_api.html', {'hotels': hotels})
