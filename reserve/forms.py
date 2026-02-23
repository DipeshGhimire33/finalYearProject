
from django import forms
from .models import Booking, Guide, Customer, Review,Hotel
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class GuideForm(forms.ModelForm):
    class Meta:
        model = Guide
        fields = ['first_name', 'last_name', 'email', 'phone',  'experience_years', ]


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
    
    

    
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone']

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
            'package',
            'guide',
            'hotel',
            'travel_date',
            'number_of_people'
        ]

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
        }





