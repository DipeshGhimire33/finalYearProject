from django.urls import path
from . import views

urlpatterns = [
    # General
    path('',                          views.index,            name='index'),
    path('base/',                     views.base,             name='base'),
    path('dashboard/',                views.dashboard,        name='dashboard'),

    # Auth
    path('register/',                 views.register,         name='register'),

    # Hotels
    path('hotels/',                   views.HotelList,        name='hotels'),
    path('hotel/register/',           views.HotelRegistration,name='hotel_registration'),
    path('hotel/edit/<int:pk>/',      views.EditHotel,        name='edit_hotel'),
    path('hotel/delete/<int:pk>/',    views.deleteHotel,      name='delete_hotel'),
    path('hotel/book/<int:hotel_id>/',views.book_room,        name='book_room'),

    # Guides
    path('guide/delete/<int:pk>/',    views.deleteGuide,      name='delete_guide'),

    # Bookings
    # FIX: was cancel_booking/ with no param — now includes <int:booking_id>
    path('booknow/',                   views.booknow,          name='booknow'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/success/<int:booking_id>/',views.booking_success, name='booking_success'),

    # Search
    path('search/',                   views.search,           name='search'),

    # Profiles
    path('customer/details/',         views.customerDetails,  name='customer_details'),
    path('hotel_owner/details/',      views.hotelOwnerdetails,name='hotel_owner_details'),

    # Static pages
    path('destinations/<int:id>/', views.destinations, name='destinations'),
    path('comments/',                 views.comments,         name='comments'),
    path('gallery/',                  views.gallery,          name='gallery'),

    path('packages/',                 views.packages,         name='packages'),
    path('about_us/',                 views.about_us,         name='about_us'),
    path('contact_us/',               views.contact_us,       name='contact_us'),

    path(
        'equipment/',
        views.equipment,
        name='equipment'
    ),


    # ADD TO CART
    path(
        'equipment/add/<int:id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),


    # REMOVE FROM CART
    path(
        'equipment/remove/<int:id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

path(
    'create-package/',
    views.create_package,
    name='create_package'
),

    path('payment/',                  views.payment,          name='payment'),
path(
    "payment-success/",
    views.payment_success,
    name="payment_success"
),

path(
    "booking-success/<int:booking_id>/",
    views.booking_success,
    name="booking_success"
),



   

    # Map / Trip
    path('maps/',                     views.maps,             name='maps'),
    path('create-trip/',              views.create_trip,      name='create_trip'),
    # FIX: single route() definition with trip_id — no duplicate plain /route/
    path('route/<int:trip_id>/',      views.route,            name='route'),
]