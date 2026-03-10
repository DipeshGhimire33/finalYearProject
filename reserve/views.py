# Create your views here.
import os
from urllib import request
from django.conf import settings
from dotenv import load_dotenv
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomerRegistrationForm, HotelRegistrationForm
from .models import Customer, Hotel, HotelOwner, UserProfile, Room, Guide, Booking
from django.core.mail import send_mail

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

def HotelList(request):
    hotels=Hotel.objects.all().order_by('-rating')  # Get all hotels ordered by rating 
    return render(request, 'hotels.html', {'hotels': hotels})

@login_required
def HotelRegistration(request):
    if request.method == "POST":
        form = HotelRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, "Hotel registered successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = HotelRegistrationForm()

    return render(request, 'hotel_reg_form.html', {'form': form})

def search(request):
    query = request.GET.get('search')
    if query:
        hotel = Hotel.objects.filter(name__icontains=query)
    else:
        hotel = Hotel.objects.all()
    
    return render(request, 'search.html', {'query': query, 'hotel': hotel})


@login_required
def EditHotel(request, pk):
    hotel = get_object_or_404(Hotel, id=pk)
    if request.method == "POST":
        form = HotelRegistrationForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = HotelRegistrationForm(instance=hotel)

    return render(request, 'hotel_reg_form.html', {'form': form})

@login_required
def book_room(request, hotel_id):
 
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel, available_rooms__gt=0)
    guides = Guide.objects.filter(is_available=True)
    
    if request.method == 'POST':
        # Get form data
        room_id = request.POST.get('room_id')
        guide_id = request.POST.get('guide_id')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        num_rooms = int(request.POST.get('num_rooms', 1))
        
        room = get_object_or_404(Room, id=room_id)
        
        # Check if enough rooms available
        if room.available_rooms < num_rooms:
            messages.error(request, 'Not enough rooms available!')
            return redirect('book_room', hotel_id=hotel_id)
        
        # Calculate total
        from datetime import datetime
        nights = (datetime.strptime(check_out, '%Y-%m-%d') - 
                 datetime.strptime(check_in, '%Y-%m-%d')).days
        total = room.price * nights * num_rooms
        
        # Add guide cost if selected
        guide = None
        if guide_id:
            guide = get_object_or_404(Guide, id=guide_id)
            total += guide.price * nights
        
        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            hotel=hotel,
            room=room,
            guide=guide,
            check_in=check_in,
            check_out=check_out,
            num_rooms=num_rooms,
            total_price=total
        )
        
        # DECREASE ROOM COUNT
        room.available_rooms -= num_rooms
        room.save()
        
        messages.success(request, f'Booking confirmed! Please check your email for booking details. Total: ${total}')
        send_mail(
            subject='Booking Confirmation',
            message=f'Your booking for {booking.room} is confirmed!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        
        messages.success(request, 'Booking confirmed! Email sent.')
        return redirect('booking_success', booking_id=booking.id)
    
    return render(request, 'booking_form.html', {
        'hotel': hotel,
        'rooms': rooms,
        'guides': guides
    })

@login_required
def cancel_booking(request, booking_id):
    """Cancel booking and restore rooms"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # INCREASE ROOM COUNT BACK
    booking.room.available_rooms += booking.num_rooms
    booking.room.save()
    
    booking.delete()
    messages.success(request, 'Booking cancelled!')
    return redirect('hotels')

@login_required
def deleteHotel(request, pk):
    if request.method == "POST":
        hotel = get_object_or_404(Hotel, id=pk,user=request.user)
        hotel.delete()
        messages.success(request, "Hotel deleted successfully!")
    return redirect('hotels')

@login_required
def deleteGuide(request, pk):
    if request.method == "POST":
        guide = get_object_or_404(Guide, id=pk,user=request.user)
        guide.delete()
        messages.success(request, "Guide deleted successfully!")
    return redirect('dashboard')

@login_required
def customerDetails(request):
    customer = get_object_or_404(user=request.user)
    return render(request, 'customer_details.html', {'customer': customer})

def hotelOwnerdetails(request):
    hotel_owner = get_object_or_404(HotelOwner, user=request.user)
    return render(request, 'hotel_owner_details.html', {'hotel_owner': hotel_owner})



