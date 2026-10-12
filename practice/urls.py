from django.urls import path

from .views import (
    home,
    practice_detail,
    questions_index,
    subject_detail,
    subject_questions,
)

urlpatterns = [
    path("", home, name="home"),
    path("questions/", questions_index, name="questions_index"),
    path("questions/<slug:slug>/", subject_questions, name="subject_questions"),
    path("subject/<slug:slug>/", subject_detail, name="subject_detail"),
    path("subject/<slug:slug>/practice/<int:practice_number>/", practice_detail, name="practice_detail"),
]
