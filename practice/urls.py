from django.urls import path

from .views import home, practice_detail, subject_detail

urlpatterns = [
    path("", home, name="home"),
    path("subject/<slug:slug>/", subject_detail, name="subject_detail"),
    path("subject/<slug:slug>/practice/<int:practice_number>/", practice_detail, name="practice_detail"),
]
