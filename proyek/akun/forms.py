from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )
    password = forms.CharField(
        widget= forms.PasswordInput(
            attrs={
                'class':'form-control'
            }
        )
    )

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )
    email = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )
    class Meta:
        model = User
        fields = ('username','email','operator')