from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Voter, Candidate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .forms import VoterRegistrationForm, VoterVerificationForm
from django.db.models import Q
from .decorators import group_required
from django.utils import timezone
from django.core.mail import send_mail
import logging
from django_ratelimit.decorators import ratelimit

audit_logger = logging.getLogger('audit')


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


@group_required('VoterRegistrars')
def register_voter(request):
    if request.method == "POST":
        form = VoterRegistrationForm(request.POST)
        if form.is_valid():
            voter = form.save(commit=False)
            voter.registered_by = request.user
            voter.save()
            # Log the voter registration
            audit_logger.info(f"Voter registered: {voter.national_id} by {request.user.username}")
            # Send email notification if email is provided
            if voter.email:
                send_mail(
                    'Voter Registration Successful',
                    f'Dear {voter.name},\n\nYou have been successfully registered as a voter in the VotingApp system.',
                    'kimeddy254@gmail.com',  # Use the same as EMAIL_HOST_USER
                    [voter.email],
                    fail_silently=True,
                )
            messages.success(request, "Voter registered successfully.")
            return redirect('Evoting:voter_list')
    else:
        form = VoterRegistrationForm()
    return render(request, "register.html", {"form": form})


@group_required('VoterRegistrars')
def verify_voter(request, voter_id):
    voter = get_object_or_404(Voter, id=voter_id)
    if voter.registered_by != request.user:
        return HttpResponse("You are not authorized to verify this voter.", status=403)
    if request.method == 'POST':
        voter.is_verified = True
        voter.verified_by = request.user
        voter.verified_at = timezone.now()
        voter.save()
        # Send verification email
        if voter.email:
            send_mail(
                'Voter Verification Successful',
                f'Dear {voter.name},\n\nYour voter registration has been verified. You are now eligible to vote in the VotingApp system.',
                'kimeddy254@gmail.com',
                [voter.email],
                fail_silently=True,
            )
        messages.success(request, "Voter verified successfully.")
        return redirect('Evoting:voter_list')
    return render(request, 'verify_voter.html', {'voter': voter})




@group_required('VotingClerks')
@ratelimit(key='ip', rate='5/m', block=True)
def vote(request):
    positions = Candidate.objects.values_list('position', flat=True).distinct()
    candidates_by_position = {}
    for position in positions:
        candidates_by_position[position] = Candidate.objects.filter(position=position)

    already_voted = False
    voters = Voter.objects.all()  # Add this line

    if request.method == "POST":
        national_id = request.POST.get('national_id')
        try:
            voter = Voter.objects.get(national_id=national_id)
            if voter.has_voted:
                messages.error(request, "You have already voted.")
                already_voted = True
            else:
                # Process a vote for each position
                for position in positions:
                    candidate_id = request.POST.get(f'candidate_{position}')
                    if candidate_id:
                        candidate = Candidate.objects.get(id=candidate_id)
                        candidate.votes += 1
                        candidate.save()
                voter.has_voted = True
                voter.save()
                messages.success(request, "Vote cast successfully.")
                if voter.email:
                    send_mail(
                        'Vote Cast Confirmation',
                        f'Dear {voter.name},\n\nYour vote has been recorded successfully in the VotingApp system.',
                        'kimeddy254@gmail.com',
                        [voter.email],
                        fail_silently=True,
                    )
        except Voter.DoesNotExist:
            messages.error(request, "Voter not registered.")
    return render(request, "vote.html", {
        "candidates_by_position": candidates_by_position,
        "already_voted": already_voted,
        "voters": voters,  # Pass voters to template
    })


@login_required
def results(request):
    # Get all unique positions
    positions = Candidate.objects.values_list('position', flat=True).distinct()
    results_by_position = {}
    for position in positions:
        results_by_position[position] = Candidate.objects.filter(position=position).order_by('-votes')
    return render(request, "results.html", {"results_by_position": results_by_position})


@staff_required
def home_view(request):
    return render(request, 'index.html')


@staff_required
def index(request):
    return render(request, 'index.html')


def candidates_by_position(request):
    presidents = Candidate.objects.filter(position='President')
    governors = Candidate.objects.filter(position='Governor')
    # Add more positions as needed
    return render(request, 'your_template.html', {
        'presidents': presidents,
        'governors': governors,
        


    })


@login_required
def voter_list(request):
    query = request.GET.get('q', '')
    voters = Voter.objects.all()
    if query:
        voters = voters.filter(
            Q(name__icontains=query) | Q(national_id__icontains=query)
        )
    return render(request, 'voter_list.html', {'voters': voters})


@user_passes_test(lambda u: u.is_staff)
def staff_dashboard(request):
    # You can add more context as needed
    return render(request, 'staff_dashboard.html')