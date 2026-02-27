from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("base/", views.base, name="base"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("hotel/register/", views.HotelRegistration, name="hotel_registration"),
    path("hotel/edit/<int:pk>/", views.EditHotel, name="edit_hotel"),
    path("hotels/", views.HotelList, name="hotels"),
    path("search/", views.search, name="search"),
    path("hotel/book/<int:hotel_id>/", views.book_room, name="book_room"),
    path("cancel_booking/", views.cancel_booking, name="cancel_booking"),
    path("customer/details/", views.customerDetails, name="customer_details"),
    path('hotel_owner/details/', views.hotelOwnerdetails, name='hotel_owner_details'),
    #path("reserve/", views.reserve, name="reserve"),
    
] 