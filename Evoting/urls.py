from django.urls import path
from . import views

app_name = 'Evoting'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_voter, name='register_voter'),  
    path('vote/<str:faculty>/', views.vote, name='vote'),
    path('results/', views.results, name='results'),
    path('home/', views.home_view, name='home'),
    path('verify/<int:national_id>/', views.verify_voter, name='verify_voter'),
    path('voters/', views.voter_list, name='voter_list'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('generate_pdf/<int:national_id>/', views.generate_pdf, name='generate_pdf'),
    path('vote/', views.select_faculty, name='select_faculty'),
    
]
