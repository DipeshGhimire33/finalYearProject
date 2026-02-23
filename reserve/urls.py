from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("base/", views.base, name="base"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("hotels_api/", views.hotelsAPI, name="hotels_api"),
    #path("reserve/", views.reserve, name="reserve"),
    
]