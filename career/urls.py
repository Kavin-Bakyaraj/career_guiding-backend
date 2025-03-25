from django.urls import path
from . import views

urlpatterns = [
    path('generate-roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('learning-resources/', views.get_learning_resources, name='learning_resources'),
    path('job-matches/', views.match_jobs, name='job_matches'),
    path('analyze-resume/', views.analyze_resume, name='analyze_resume'),
    path('career-trends/', views.get_career_trends, name='career_trends'),
]