from django.db import models
from django.conf import settings
from datetime import date

# Create your models here.
FACULTY_CHOICES = [
    ('Engineering', 'Engineering'),
    ('Arts', 'Arts'),
    ('Science', 'Science'),
    ('Commerce', 'Commerce'),
    ('Law', 'Law'),
    ('Medicine', 'Medicine'),
]
class Voter(models.Model):
    national_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)  # New field
    age = models.PositiveIntegerField(null=True, blank=True)  # New field
    constituency = models.CharField(max_length=100, null=True, blank=True)  # New field
    has_voted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # Add this field
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='registered_voters'
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_voters'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    voted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='voted_voters'
    )
    voted_at = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    faculty = models.CharField(
        max_length=50, choices=FACULTY_CHOICES, null=True, blank=True
    )  # New field for faculty
    

    def __str__(self):
        return f"{self.name} ({self.national_id})"

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            today = date.today()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        super().save(*args, **kwargs)

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    party = models.CharField(max_length=100, default='')  # Party the candidate represents
    position = models.CharField(max_length=100, default='')  # Position the candidate is vying for
    votes = models.PositiveIntegerField(default=0)
    is_faculty_representative = models.BooleanField(default=True)  # New field for faculty representative
    # Filter for general candidates
    faculty = models.CharField(
        max_length=50, choices=FACULTY_CHOICES, null=True, blank=True
    )  # New field for faculty

    def __str__(self):
        return f"{self.name} ({self.party}) - {self.position}"

# Example Vote model
class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.voter.name} voted for {self.candidate.name} at {self.voted_at}"
