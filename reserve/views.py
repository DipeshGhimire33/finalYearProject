import os
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from dotenv import load_dotenv
from decimal import Decimal
from django.db.models import Avg, Count, Sum , Q
from .forms import CustomerRegistrationForm, HotelRegistrationForm, HotelReviewForm
from .models import *
from reserve import models
from django.http import HttpResponseForbidden

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


# ---------------------------------------------------------------------------
# General pages
# ---------------------------------------------------------------------------





from django.db.models import Count, Avg

def index(request):
    destinations = Destination.objects.all()

    reviews = AppReview.objects.select_related('user')
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    top_review = reviews.order_by('-rating', '-created_at').first()

    latest_experiences = DestinationExperience.objects.order_by('-created_at')[:10]

    # Top destinations based on completed bookings
    top_packages = (
        Booking.objects
        .values("trip__destination")
        .annotate(
            total_bookings=Count("id"),
            average_cost=Avg("total_price"),
            average_days=Avg("trip__days"),
        )
        .order_by("-total_bookings")[:6]
    )

    context = {
        "destinations": destinations,
        "average_rating": round(average_rating, 1),
        "top_review": top_review,
        "latest_experiences": latest_experiences,
        "top_packages": top_packages,
    }

    return render(request, "index.html", context)


def base(request):
    return render(request, 'base.html')



def destinations(request,id):
    destination = get_object_or_404(Destination, id=id)

    context = {
        "destination": destination,
        "popular_places": destination.popular_places.all(),
        "must_visit_places": destination.must_visit_places.all(),
    }

    return render(request, "destinations.html", context)

def comments(request):

    if request.method == "POST":
        AppReview.objects.create(
            user=request.user,
            rating=int(request.POST.get("rating")),
            comment=request.POST.get("comment")
        )
        return redirect("comments")  # IMPORTANT refresh

    # 🔥 ALWAYS fetch fresh data
    reviews = AppReview.objects.all().order_by("-created_at")

    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    if average_rating is None:
        average_rating = 0

    top_review = reviews.order_by("-rating", "-created_at").first()

    return render(request, "comments.html", {
        "reviews": reviews,
        "average_rating": round(average_rating, 1),
        "top_review": top_review
    })


def best_packages(request):
    packages = Package.objects.annotate(
        booking_count=Count("booking")
    ).order_by("-booking_count")

    return render(request, "best_packages.html", {
        "packages": packages
    })


def gallery(request):
    if request.method == "POST":
        destination = Destination.objects.get(id=request.POST.get("destination"))

        DestinationExperience.objects.create(
            user=request.user,
            destination=destination,
            image=request.FILES.get("image"),
            caption=request.POST.get("caption")
        )

        return redirect("gallery")

    experiences = DestinationExperience.objects.select_related(
        "user", "destination"
    ).order_by("-created_at")

    destinations = Destination.objects.all()

    return render(request, "gallery.html", {
        "experiences": experiences,
        "destinations": destinations,
    })



def about_us(request):
    return render(request, 'about_us.html')


from django.contrib import messages

def contact_us(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )

        messages.success(request, "Message sent successfully!")
        return redirect("contact_us")

    return render(request, "contact_us.html")



def book_hotel(request, hotel_id):

    hotel = get_object_or_404(
        Hotel,
        id=hotel_id
    )

    rooms = hotel.rooms.all()
    guides = Guide.objects.all()


    if request.method == "POST":

        room_id = request.POST.get("room_id")

        data = {

            "hotel_id": hotel.id,

            "room_id": room_id,

            "check_in": request.POST.get("check_in"),

            "check_out": request.POST.get("check_out"),

            "num_rooms": request.POST.get("num_rooms"),

            "guide_id": request.POST.get("guide_id"),

        }


        request.session["hotel_choice"] = data


        return redirect("equipment")



    return render(
        request,
        "book_hotel.html",
        {
            "hotel": hotel,
            "rooms": rooms,
            "guides": guides
        }
    )

@login_required
def book_room(request, hotel_id):

    hotel = get_object_or_404(
        Hotel,
        id=hotel_id
    )

    rooms = Room.objects.filter(
        hotel=hotel,
        available_rooms__gt=0
    )

    guides = Guide.objects.filter(
        is_available=True
    )


    if request.method == "POST":

        room_id = request.POST.get("room_id")
        guide_id = request.POST.get("guide_id")

        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        num_rooms = int(
            request.POST.get(
                "num_rooms",
                1
            )
        )


        room = get_object_or_404(
            Room,
            id=room_id
        )


        if room.available_rooms < num_rooms:

            messages.error(
                request,
                "Not enough rooms available"
            )

            return redirect(
                "book_room",
                hotel_id=hotel.id
            )


        guide = None

        if guide_id:
            guide = get_object_or_404(
                Guide,
                id=guide_id
            )


        # SAVE HOTEL BOOKING TABLE

        hotel_booking = HotelBooking.objects.create(

            user=request.user,

            hotel=hotel,

            room=room,

            guide=guide,

            check_in=check_in,

            check_out=check_out,

            num_rooms=num_rooms

        )


        # reduce room count

        room.available_rooms -= num_rooms
        room.save()



        # store for next step
        request.session["hotel_choice"] = {

            "hotel_booking_id": hotel_booking.id,

            "hotel_id": hotel.id,

            "room_id": room.id,

            "check_in": check_in,

            "check_out": check_out,

            "num_rooms": num_rooms

        }


        return redirect(
            "equipment"
        )



    return render(
        request,
        "book_hotel.html",
        {
            "hotel":hotel,
            "rooms":rooms,
            "guides":guides
        }
    )

def equipment(request):

    equipments = Equipment.objects.all()

    cart = request.session.get("cart", [])

    cart_ids = [item["id"] for item in cart]

    for equipment in equipments:
        equipment.in_cart = equipment.id in cart_ids

    total_cost = sum(
        item["price"] * item["qty"]
        for item in cart
    )

    return render(
        request,
        "equipment.html",
        {
            "equipments": equipments,
            "cart": cart,
            "total_cost": total_cost,
        }
    )

def add_to_cart(request, id):

    equipment = get_object_or_404(Equipment, id=id)

    cart = request.session.get("cart", [])

    for item in cart:

        if item["id"] == equipment.id:

            item["qty"] += 1
            break

    else:

        cart.append({
            "id": equipment.id,
            "name": equipment.name,
            "price": float(equipment.price_per_day),
            "qty": 1
        })


    request.session["cart"] = cart
    request.session.modified = True

    return redirect("equipment")

def remove_from_cart(request, id):

    cart = request.session.get("cart", [])

    cart = [item for item in cart if item["id"] != id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("equipment")

def create_package(request):

    hotel = request.session.get(
        "hotel_choice"
    )

    cart = request.session.get(
        "cart",
        []
    )


    if not hotel:

        return redirect("index")


    # if not cart:

    #     return redirect("equipment")


    return redirect("packages")


import math


def calculate_distance(lat1, lng1, lat2, lng2):

    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat/2)**2
        +
        math.cos(math.radians(lat1))
        *
        math.cos(math.radians(lat2))
        *
        math.sin(dlng/2)**2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1-a)
    )

    return round(R * c, 2)



def packages(request):

    trip = Trip.objects.filter(
        user=request.user
    ).order_by("-id").first()


    if not trip:
        return redirect("route")


    hotel_data = request.session.get(
        "hotel_choice"
    )


    if not hotel_data:
        return redirect("hotel")


    hotel = Hotel.objects.get(
        id=hotel_data["hotel_id"]
    )


    room = Room.objects.get(
        id=hotel_data["room_id"]
    )

    vehicle = Vehicle.objects.get(
        id=1
    )  # Assuming you have a Vehicle model and want to get the first vehicle

    cart = request.session.get(
        "cart",
        []
    )


    # equipment cost

    equipment_cost = Decimal(0)

    for item in cart:

        equipment_cost += (
        Decimal(str(item["price"]))
        *
        item["qty"]
        *
        trip.days
        )



    # vehicle cost

    distance = calculate_distance(
        trip.pickup_lat,
        trip.pickup_lng,
        trip.destination_lat,
        trip.destination_lng
    )


    if trip.people <= 15:

        rate = 10

    else:

        rate = 50


    if vehicle:
        vehicle_cost =int(Decimal(str(distance * rate)))
    else:
        vehicle_cost = 0



    # hotel cost

    hotel_cost = (
        room.price
        *
        int(hotel_data["num_rooms"])
        *
        trip.days
    )



    total_cost = int((
        hotel_cost
        +
        equipment_cost
        +
        vehicle_cost
    ))



    return render(
        request,
        "packages.html",
        {

            "trip": trip,

            "hotel": hotel,

            "room": room,

            "nr": hotel_data["num_rooms"],

            "cart": cart,

            "days": trip.days,

            "distance": distance,

            "vehicle": vehicle,

            "vehicle_rate": rate,

            "vehicle_cost": vehicle_cost,

            "hotel_cost": hotel_cost,

            "equipment_cost": equipment_cost,

            "total_cost": total_cost,

        }
    )


def payment(request):
    return render(request, 'payment.html')

def route(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    hotels = Hotel.objects.filter(location__icontains=trip.destination, available_rooms__gt=0)
    if not hotels.exists():
        hotels = Hotel.objects.filter(available_rooms__gt=0)[:6]
    return render(request, "route.html", {"trip": trip, "hotels": hotels})

def payment_success(request):

    trip = Trip.objects.filter(
        user=request.user
    ).order_by("-id").first()


    hotel_data = request.session.get("hotel_choice")

    cart = request.session.get("cart", [])


    if not trip or not hotel_data:
        return redirect("packages")


    hotel = get_object_or_404(
        Hotel,
        id=hotel_data["hotel_id"]
    )


    room = get_object_or_404(
        Room,
        id=hotel_data["room_id"]
    )


    # -----------------------
    # HOTEL COST
    # -----------------------

    hotel_cost = (
        room.price *
        int(hotel_data["num_rooms"]) *
        trip.days
    )


    # -----------------------
    # EQUIPMENT COST
    # -----------------------

    equipment_cost = 0

    for item in cart:

        equipment_cost += (
            item["price"]
            *
            item["qty"]
            *
            trip.days
        )


    # -----------------------
    # VEHICLE COST
    # -----------------------

    distance = calculate_distance(
        trip.pickup_lat,
        trip.pickup_lng,
        trip.destination_lat,
        trip.destination_lng
    )


    if trip.people <= 15:
        rate = 10
    else:
        rate = 50


    vehicle_cost = Decimal(str(distance * rate))



    total = (
    Decimal(hotel_cost)
    +
    Decimal(equipment_cost)
    +
    Decimal(vehicle_cost)
)


    # -----------------------
    # FINAL BOOKING
    # -----------------------

    booking = Booking.objects.create(

        user=request.user,

        trip=trip,

        hotel=hotel,

        room=room,

        check_in=hotel_data["check_in"],

        check_out=hotel_data["check_out"],

        num_rooms=int(hotel_data["num_rooms"]),

        people=trip.people,

        distance_km=distance,

        vehicle_cost=vehicle_cost,

        total_price=total,

        payment_status=True

    )



    # -----------------------
    # SAVE EQUIPMENT
    # -----------------------

    for item in cart:

        BookingEquipment.objects.create(

            booking=booking,

            equipment_id=item["id"],

            quantity=item["qty"]

        )


    # clear temporary session

    request.session.pop("cart", None)

    request.session.pop(
        "hotel_choice",
        None
    )


    return redirect(
        "booking_success",
        booking_id=booking.id
    )


def maps(request):
    return render(request, 'maps.html')

def booknow(request):
    return render(request, 'booknow.html')

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@login_required
def admin_dashboard(request):


    total_revenue = Booking.objects.aggregate( total=Sum("total_price"))["total"] or 0

    total_bookings = Booking.objects.count()

    hotel_count = Hotel.objects.count()

    customer_count = Customer.objects.count()

    top_destinations = (
    Booking.objects
    .values("trip__destination")
    .annotate(
        bookings=Count("id"),
        avg_price=Avg("total_price")
    )
    .order_by("-bookings")[:5]
    )

    recent_bookings = Booking.objects.select_related(
    "user",
    "trip",
    "hotel"
    ).order_by("-id")[:10]

    BookingEquipment.objects.values(
    "equipment__name"
    ).annotate(
    total=Count("id")
    ).order_by("-total")

    Booking.objects.values(
    "hotel__name"
    ).annotate(
    total=Count("id")
    ).order_by("-total")

    popular_hotels = (
    Booking.objects
    .values("hotel__name")
    .annotate(
        total=Count("id")
    )
    .order_by("-total")[:5]
)
    
    popular_equipment = (
    BookingEquipment.objects
    .values("equipment__name")
    .annotate(
        total=Count("id")
    )
    .order_by("-total")[:5]
)
    

    
    latest_gallery=(DestinationExperience.objects.order_by(
    "-created_at"
)[:6])
    
    latest_messages=(ContactMessage.objects.order_by(
    "-id"
)[:5])
    
    latest_reviews = AppReview.objects.select_related("user").order_by("-created_at")[:5]
    

    context = {

        "total_revenue": total_revenue,

        "total_bookings": total_bookings,

        "hotel_count": hotel_count,

        "customer_count": customer_count,

        "recent_bookings": recent_bookings,

        "top_destinations": top_destinations,

        "popular_hotels": popular_hotels,

        "popular_equipment": popular_equipment,

        "latest_reviews": latest_reviews,

        "messages": latest_messages,

        "gallery": latest_gallery,

    }

    return render(
        request,
        "dashboard.html",
        context
    )

@login_required
def hotel_owner_dashboard(request):

    my_hotels = Hotel.objects.filter(owner=request.user)

    bookings = Booking.objects.filter(
        hotel__in=my_hotels
    )

    total_revenue = bookings.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    total_bookings = bookings.count()

    hotel_count = my_hotels.count()

    customer_count = (
        bookings.values("user")
        .distinct()
        .count()
    )

    top_destinations = (
        bookings.values("trip__destination")
        .annotate(
            bookings=Count("id"),
            avg_price=Avg("total_price")
        )
        .order_by("-bookings")[:5]
    )

    recent_bookings = (
        bookings
        .select_related(
            "user",
            "trip",
            "hotel"
        )
        .order_by("-id")[:10]
    )

    popular_hotels = (
        bookings
        .values("hotel__name")
        .annotate(
            total=Count("id")
        )
        .order_by("-total")
    )

    popular_equipment = (
        BookingEquipment.objects
        .filter(
            booking__hotel__in=my_hotels
        )
        .values("equipment__name")
        .annotate(
            total=Count("id")
        )
        .order_by("-total")[:5]
    )

    latest_reviews = (
        HotelReview.objects
        .filter(
            hotel__in=my_hotels
        )
        .select_related(
            "user",
            "hotel"
        )
        .order_by("-created_at")[:5]
    )

    context = {

        "total_revenue": total_revenue,

        "total_bookings": total_bookings,

        "hotel_count": hotel_count,

        "customer_count": customer_count,

        "recent_bookings": recent_bookings,

        "top_destinations": top_destinations,

        "popular_hotels": popular_hotels,

        "popular_equipment": popular_equipment,

        "latest_reviews": latest_reviews,

    }

    return render(
        request,
        "hotel_owner_dashboard.html",
        context,
    )

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return admin_dashboard(request)

    elif request.user.groups.filter(name="HotelOwner").exists():
        return hotel_owner_dashboard(request)

    return redirect("index")

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def register(request):

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password1'])
            user.save()

            # OPTIONAL: auto-login
            login(request, user)

            messages.success(request, "Account created successfully!")

            return redirect('index')  # everyone starts as customer

        else:
            messages.error(request, 'Please fix the errors below.')

    else:
        form = CustomerRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


# ---------------------------------------------------------------------------
# Hotel
# ---------------------------------------------------------------------------


def HotelList(request):
    hotels = Hotel.objects.annotate(
        avg_rating=Avg("hotelreview__rating")
    )

    return render(request, "hotels.html", {
        "hotels": hotels
    })

def rate_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == "POST":
        form = HotelReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.hotel = hotel
            review.user = request.user
            review.save()

            return redirect('hotels')

    else:
        form = HotelReviewForm()

    return render(request, "rate_hotel.html", {
        "hotel": hotel,
        "form": form
    })


def search_hotels(request):
    query = request.GET.get('query', '').strip()

    hotels = Hotel.objects.all()

    if query:
        hotels = hotels.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(address__icontains=query)
        )

    hotels = hotels.annotate(
        avg_rating=Avg("hotelreview__rating")
    )

    return render(request, "hotels.html", {
        "hotels": hotels,
        "query": query
    })

@login_required
def HotelRegistration(request):

    # only hotel owners allowed
    if not request.user.groups.filter(name="HotelOwner").exists():
        return HttpResponseForbidden("Only hotel owners can register hotels")

    if request.method == 'POST':
        form = HotelRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user   # IMPORTANT FIX
            hotel.save()

            messages.success(request, 'Hotel registered successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = HotelRegistrationForm()

    return render(request, 'hotel_reg_form.html', {'form': form})

def search(request):
    query = request.GET.get('search', '')

    hotels = Hotel.objects.filter(
        name__icontains=query
    ) if query else Hotel.objects.all()

    return render(request, 'search.html', {
        'query': query,
        'hotel': hotels
    })

@login_required
def EditHotel(request, pk):

    hotel = get_object_or_404(Hotel, id=pk)

    # only owner of hotel OR admin
    if not request.user.is_superuser and hotel.owner != request.user:
        return HttpResponseForbidden("You are not allowed to edit this hotel")

    if request.method == 'POST':
        form = HotelRegistrationForm(request.POST, request.FILES, instance=hotel)

        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = HotelRegistrationForm(instance=hotel)

    return render(request, 'hotel_reg_form.html', {'form': form})


@login_required
def deleteHotel(request, pk):

    hotel = get_object_or_404(Hotel, id=pk)

    # only owner or admin
    if not request.user.is_superuser and hotel.owner != request.user:
        return HttpResponseForbidden("You cannot delete this hotel")

    if request.method == 'POST':
        hotel.delete()
        messages.success(request, 'Hotel deleted successfully!')

    return redirect('hotels')

# ---------------------------------------------------------------------------
# Guide
# ---------------------------------------------------------------------------

@login_required
def deleteGuide(request, pk):
    if request.method == 'POST':
        # FIX: Guide has no user field — removed user=request.user filter
        guide = get_object_or_404(Guide, id=pk)
        guide.delete()
        messages.success(request, 'Guide deleted successfully!')
    return redirect('dashboard')


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------



@login_required
def cancel_booking(request, booking_id):
    # FIX: was missing booking_id param — now correctly received from URL
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    booking.room.available_rooms += booking.num_rooms
    booking.room.save()
    booking.delete()

    messages.success(request, 'Booking cancelled!')
    return redirect('hotels')


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_success.html', {'booking': booking})


# ---------------------------------------------------------------------------
# Customer / Owner profile
# ---------------------------------------------------------------------------

@login_required
def customerDetails(request):
    # FIX: was get_object_or_404(user=request.user) — missing model arg
    customer = get_object_or_404(Customer, user=request.user)
    return render(request, 'customer_details.html', {'customer': customer})


@login_required
def hotelOwnerdetails(request):
    hotel_owner = get_object_or_404(HotelOwner, user=request.user)
    return render(request, 'hotel_owner_details.html', {'hotel_owner': hotel_owner})


# ---------------------------------------------------------------------------
# Trip / Map  (FIX: removed duplicate route() definition)
# ---------------------------------------------------------------------------

def create_trip(request):
    """
    Two entry points:

    1. booknow form (no coords yet):
       pickup + destination text only → save Trip → redirect to maps
       maps.html reads the GET params, pre-fills the search boxes,
       auto-geocodes both locations, and shows the "View Route & Hotels" button.

    2. maps.html "View Route & Hotels" form (coords confirmed):
       all fields including lat/lng → save Trip → redirect to route/<id>/
    """
    if request.method == 'GET':
        pickup          = request.GET.get('pickup', '').strip()
        destination     = request.GET.get('destination', '').strip()
        pickup_lat      = request.GET.get('pickup_lat', '').strip()
        pickup_lng      = request.GET.get('pickup_lng', '').strip()
        destination_lat = request.GET.get('destination_lat', '').strip()
        destination_lng = request.GET.get('destination_lng', '').strip()
        people          = request.GET.get('people', '1').strip()
        days            = request.GET.get('days', '1').strip()

        if not pickup or not destination:
            messages.error(request, 'Please enter both pickup and destination.')
            return redirect('maps')

        try:
            people_int = int(people)
            days_int   = int(days)
        except ValueError:
            messages.error(request, 'People and days must be numbers.')
            return redirect('maps')

        has_coords = pickup_lat and pickup_lng and destination_lat and destination_lng

        if has_coords:
            # Coming from maps.html — save full trip and go to route summary
            trip = Trip.objects.create(
                user            = request.user if request.user.is_authenticated else None,
                fullname        = request.GET.get('fullname', ''),
                email           = request.GET.get('email', ''),
                pickup          = pickup,
                destination     = destination,
                pickup_lat      = float(pickup_lat),
                pickup_lng      = float(pickup_lng),
                destination_lat = float(destination_lat),
                destination_lng = float(destination_lng),
                people          = people_int,
                days            = days_int,
            )
            return redirect('route', trip_id=trip.id)

        else:
            # Coming from booknow form — no coords yet.
            # Don't save a trip yet; just send the user to maps with their
            # text pre-filled so they can confirm the route on the map first.
            from urllib.parse import urlencode
            params = urlencode({
                'pickup':      pickup,
                'destination': destination,
                'fullname':    request.GET.get('fullname', ''),
                'email':       request.GET.get('email', ''),
                'people':      people_int,
                'days':        days_int,
            })
            return redirect(f'/reserve/maps/?{params}')

    return redirect('maps')

