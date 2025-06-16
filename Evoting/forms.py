from django import forms
from .models import Voter

class VoterRegistrationForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['national_id', 'name', 'date_of_birth', 'age', 'constituency', 'email']
        widgets = {
            'national_id': forms.TextInput(attrs={'placeholder': 'National ID'}),
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class VoterVerificationForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = []