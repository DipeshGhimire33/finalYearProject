from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("base/", views.base, name="base"),
    #path("reserve/", views.reserve, name="reserve"),
    path("destinations/", views.destinations, name="destinations"),
    path("comments/", views.comments, name="comments"),
    path("gallery/", views.gallery, name="gallery"),
    path("packages/", views.packages, name="packages"),
    path("route/", views.route, name="route"),
    
]