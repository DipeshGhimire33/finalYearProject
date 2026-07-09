from django import forms
from .models import  Guide, Booking,Hotel #review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class GuideForm(forms.ModelForm):
    class Meta:
        model = Guide
        fields = ['name', 'location', 'email', 'phone','price_per_day','email','description','specialization','image'] 


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    

class BookingForm(forms.ModelForm):
    guide = forms.ModelChoiceField(
        queryset=Guide.objects.filter(is_available=True),
        required=False
    )

    travel_date = forms.DateField(
        widget=forms.SelectDateWidget
    )

    class Meta:
        model = Booking
        fields = [
            'hotel',
            'room',
            'check_in',
            'check_out',
            'num_rooms',
            'guide',  # Add guide selection to the booking form
        ]

# class ReviewForm(forms.ModelForm):
#     rating = forms.IntegerField(min_value=1, max_value=5)

#     class Meta:
#         model = Review
#         fields = ['rating', 'review_text']
#         widgets = {
#             'review_text': forms.Textarea(attrs={'rows': 4}),
#         }

class HotelRegistrationForm(forms.ModelForm):
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Hotel
        fields = [
            'name',
            'location',
            'address',
            'description',
            'price_per_night',
            'available_rooms',
            'image'
        ]
  





