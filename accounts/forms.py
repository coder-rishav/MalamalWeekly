from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'date_of_birth', 'address', 'city', 'state', 'postal_code', 'country', 'profile_photo']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class KYCSubmissionForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'full_name', 'aadhar_number', 'pan_number',
            'aadhar_front', 'aadhar_back', 'pan_card', 'selfie_with_id'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Full Name as per ID'
            }),
            'aadhar_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '1234 5678 9012',
                'maxlength': '12'
            }),
            'pan_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'ABCDE1234F',
                'maxlength': '10',
                'style': 'text-transform: uppercase'
            }),
            'aadhar_front': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'aadhar_back': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'pan_card': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'selfie_with_id': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        help_texts = {
            'aadhar_number': 'Enter 12-digit Aadhar number',
            'pan_number': 'Enter 10-character PAN number',
            'selfie_with_id': 'Upload a clear selfie holding your Aadhar or PAN card',
        }
    
    def clean_aadhar_number(self):
        aadhar = self.cleaned_data.get('aadhar_number')
        if aadhar:
            # Remove spaces
            aadhar = aadhar.replace(' ', '')
            if not aadhar.isdigit() or len(aadhar) != 12:
                raise forms.ValidationError('Aadhar number must be exactly 12 digits')
        return aadhar
    
    def clean_pan_number(self):
        pan = self.cleaned_data.get('pan_number')
        if pan:
            pan = pan.upper()
            if len(pan) != 10:
                raise forms.ValidationError('PAN number must be exactly 10 characters')
            # Basic PAN format validation: ABCDE1234F
            if not (pan[:5].isalpha() and pan[5:9].isdigit() and pan[9].isalpha()):
                raise forms.ValidationError('Invalid PAN format. Format should be: ABCDE1234F')
        return pan


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
