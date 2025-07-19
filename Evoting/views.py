from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Voter, Candidate, FACULTY_CHOICES
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .forms import VoterRegistrationForm, VoterVerificationForm
from django.db.models import Q
from .decorators import group_required
from django.utils import timezone
import logging
from django_ratelimit.decorators import ratelimit
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO
from django.core.mail import EmailMessage
from django.core.mail import send_mail


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
            
            audit_logger.info(f"Voter registered: {voter.national_id} by {request.user.username}")
            
            if voter.email:
                send_mail(
                    'Voter Registration Successful',
                    f'Dear {voter.name},\n\nYou have been successfully registered as a voter in the VotingApp system.',
                    'kimeddy254@gmail.com',  
                    [voter.email],
                    fail_silently=True,
                )
            messages.success(request, "Voter registered successfully.")
            return redirect('Evoting:voter_list')
    else:
        form = VoterRegistrationForm()
    return render(request, "register.html", {"form": form})


@group_required('VoterRegistrars')
def verify_voter(request, national_id):
    voter = get_object_or_404(Voter, id=national_id)
    if voter.registered_by != request.user:
        return HttpResponse("You are not authorized to verify this voter.", status=403)
    if request.method == 'POST':
        voter.is_verified = True
        voter.verified_by = request.user
        voter.verified_at = timezone.now()
        voter.save()
        
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
def vote(request, faculty):
    voter = None
    candidates_by_position = {}
    already_voted = False

    positions = Candidate.objects.filter(faculty=faculty).values_list('position', flat=True).distinct()
    for position in positions:
        candidates_by_position[position] = Candidate.objects.filter(position=position, faculty=faculty)

    voters = Voter.objects.filter(faculty=faculty)

    if request.method == "POST":
        national_id = request.POST.get('national_id')
        try:
            voter = Voter.objects.get(national_id=national_id)
            
            if voter.faculty != faculty:
                messages.error(request, "This voter does not belong to the selected faculty.")
                return redirect('vote', faculty=faculty)

            if voter.has_voted:
                messages.error(request, "You have already voted.")
                already_voted = True
            else:
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
        "faculty": faculty,
        "candidates_by_position": candidates_by_position,
        "already_voted": already_voted,
        "voters": voters,
    })


@login_required
def results(request):
    
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
    
    return render(request, 'staff_dashboard.html')



def generate_pdf(request, national_id):
    voter = get_object_or_404(Voter, id=national_id)
    template = get_template('voter_card.html')
    html = template.render({'voter': voter})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="voter_{voter.national_id}.pdf"'

    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response


def generate_pdf_buffer(voter):
    template = get_template('voter_card.html')  
    html = template.render({'voter': voter})

    buffer = BytesIO()
    result = pisa.CreatePDF(src=html, dest=buffer)

    if result.err:
        print(" PDF generation failed.")
        return None

    buffer.seek(0)
    return buffer

def send_card_by_email(request, national_id): 
    voter = get_object_or_404(Voter, id=national_id)

    if not voter.email:
        messages.error(request, "Voter does not have an email address.")
        return redirect('Evoting:voter_list')

    subject = 'Your Voter Card'
    message = get_template('voter_card.html').render({'voter': voter})

    email = send_mail(
        subject=subject,
        body=message,
        from_email=None,
        to=[voter.email],
    )
    email.content_subtype = 'html'

    
    pdf_buffer = generate_pdf_buffer(voter)
    if pdf_buffer:
        pdf_buffer.seek(0)
        email.attach(
            f'voter_{voter.national_id}.pdf',
            pdf_buffer.read(),
            'application/pdf'
        )
    else:
        messages.error(request, "PDF generation failed.")
        return redirect('Evoting:voter_list')

    try:
        email.send(fail_silently=False)
        messages.success(request, "Voter card sent successfully.")
    except Exception as e:
        messages.error(request, f"Failed to send voter card: {str(e)}")

    return redirect('Evoting:voter_list')



def select_faculty(request):
    if request.method == 'POST':
        selected_faculty = request.POST.get('faculty')
        return redirect('vote', faculty=selected_faculty)
    return render(request, 'select_faculty.html', {'faculties': FACULTY_CHOICES})
