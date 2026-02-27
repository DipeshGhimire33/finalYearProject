from django import forms
from .models import  Guide, Booking,Hotel #review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class GuideForm(forms.ModelForm):
    class Meta:
        model = Guide
        fields = ['name', 'location', 'email', 'phone','price_per_day','email','description','specialization','image'] 


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    role = forms.ChoiceField(
        choices=[
            ('customer', 'Customer'),
            ('hotel_owner', 'Hotel Owner'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}) 
        # widget=forms.RadioSelect   # shows as radio buttons, you can use Select too
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    

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
    class Meta:
        model = Hotel
        location = forms.ChoiceField(choices=[
            ('Kathmandu', 'Kathmandu'),
            ('Pokhara', 'Pokhara'),
            ('Chitwan', 'Chitwan'),
            ('Lumbini', 'Lumbini'),
            ('Mustang', 'Mustang'), 
            ('Annapurna', 'Annapurna'),
            ('Everest', 'Everest'),
            # Add more locations as needed 
            #best use the api for this
        ])
        widget=forms.Select(attrs={'class': 'form-control'}) 
            
        
        fields = ['name', 'address', 'description', 'price_per_night', 'available_rooms','image'] 







