from django import forms
from .models import Voter
from datetime import date


class VoterRegistrationForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['national_id', 'name', 'date_of_birth', 'age', 'constituency', 'email','faculty']
        widgets = {
            'national_id': forms.TextInput(attrs={'placeholder': 'Registration Number'}),
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),

            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 15:
            raise forms.ValidationError("You must be at least 15 years old to register.")
        
        # Optionally, auto-set the age field
        self.cleaned_data['age'] = age
        return dob

class VoterVerificationForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = []