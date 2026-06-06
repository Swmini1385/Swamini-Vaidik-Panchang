from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import KundaliRecord, LocationMaster

User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Email ID'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}),
        required=True
    )

    class Meta:
        model = User
        fields = ('name', 'email', 'password')

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            name=self.cleaned_data['name']
        )
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this Email ID already exists.")
        return email

class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Email ID'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your registered Email ID'})
    )

class ProfileUpdateForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'})
    )

    class Meta:
        model = User
        fields = ('name', 'email', 'phone_number')

class KundaliForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    time_of_birth = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    place_of_birth = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type to search place...', 'id': 'place_search_input', 'autocomplete': 'off'})
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_country'})
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_state'})
    )
    district = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_district'})
    )
    city_village = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_city_village'})
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_latitude', 'step': '0.000001'})
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_longitude', 'step': '0.000001'})
    )
    timezone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_timezone'})
    )

    class Meta:
        model = KundaliRecord
        fields = ('name', 'gender', 'date_of_birth', 'time_of_birth', 'place_of_birth', 'country', 'state', 'district', 'city_village', 'latitude', 'longitude', 'timezone')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
        }

class KundaliMilanForm(forms.Form):
    # Groom Details
    groom_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Groom Name'})
    )
    groom_dob = forms.DateField(
        label="Groom Date of Birth",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    groom_tob = forms.TimeField(
        label="Groom Time of Birth",
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    groom_pob = forms.CharField(
        label="Groom Place of Birth",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Pune'})
    )
    
    # Bride Details
    bride_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Bride Name'})
    )
    bride_dob = forms.DateField(
        label="Bride Date of Birth",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    bride_tob = forms.TimeField(
        label="Bride Time of Birth",
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    bride_pob = forms.CharField(
        label="Bride Place of Birth",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mumbai'})
    )

class LocationForm(forms.ModelForm):
    class Meta:
        model = LocationMaster
        fields = ('location_name', 'country', 'state', 'district', 'city_village', 'latitude', 'longitude', 'timezone')
        widgets = {
            'location_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'country': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'state': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'district': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'city_village': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.000001'}),
            'timezone': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
