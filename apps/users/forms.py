from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter strong password', 'class': 'form-input'}),
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-input'})
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'preferred_market', 'preferred_currency', 'preferred_gold_unit']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'trader@example.com', 'class': 'form-input'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'John Doe / Rajesh Sharma', 'class': 'form-input'}),
            'preferred_market': forms.Select(attrs={'class': 'form-select'}),
            'preferred_currency': forms.Select(attrs={'class': 'form-select'}),
            'preferred_gold_unit': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'trader@example.com', 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise forms.ValidationError("This account is currently disabled.")
            cleaned_data['user'] = user
        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'phone_number', 'preferred_market', 
            'preferred_currency', 'preferred_gold_unit', 
            'telegram_chat_id', 'whatsapp_number'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_market': forms.Select(attrs={'class': 'form-select'}),
            'preferred_currency': forms.Select(attrs={'class': 'form-select'}),
            'preferred_gold_unit': forms.Select(attrs={'class': 'form-select'}),
            'telegram_chat_id': forms.TextInput(attrs={'placeholder': '@your_telegram_handle or Chat ID', 'class': 'form-input'}),
            'whatsapp_number': forms.TextInput(attrs={'placeholder': '+91... or +1...', 'class': 'form-input'}),
        }
