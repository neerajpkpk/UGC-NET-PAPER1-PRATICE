from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Subject


def health(request):
    return HttpResponse("ok")


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    return HttpResponse(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /health/\n"
        f"Sitemap: {sitemap_url}\n",
        content_type="text/plain",
    )


def home(request):
    subjects = Subject.objects.all()
    subject_cards = []
    for subject in subjects:
        subject_cards.append(
            {
                "object": subject,
                "question_count": subject.total_questions,
            }
        )
    return render(
        request,
        "practice/home.html",
        {
            "subjects": subject_cards,
            "page_title": "UGC NET Paper 1 Online Practice Questions",
            "page_description": (
                "Practise UGC NET Paper 1 online with subject-wise questions. "
                "Browse available topics and start a practice session with "
                "questions, answers and explanations."
            ),
        },
    )


def subject_detail(request, slug):
    subject = Subject.objects.filter(slug=slug).first()
    if not subject:
        raise Http404("Subject does not exist.")

    practice_cards = subject.get_practice_cards()
    total_questions = subject.total_questions
    page_title = f"UGC NET {subject.name} Practice Questions"
    page_description = (
        f"Practise {subject.name} questions for UGC NET Paper 1. "
        f"There are currently {total_questions} questions available in "
        "subject-wise practice sessions."
    )

    return render(
        request,
        "practice/subject_detail.html",
        {
            "subject": subject,
            "practice_cards": practice_cards,
            "total_questions": total_questions,
            "page_title": page_title,
            "page_description": page_description,
        },
    )


def practice_detail(request, slug, practice_number):
    subject = Subject.objects.filter(slug=slug).first()
    if not subject:
        raise Http404("Subject does not exist.")

    questions = subject.get_questions_for_practice(practice_number)
    if not questions:
        raise Http404("Practice session does not exist.")

    question_payload = []
    for index, question in enumerate(questions, start=1):
        question_payload.append(
            {
                "id": question.id,
                "number": index,
                "question_text": question.question_text,
                "option_a": question.option_a,
                "option_b": question.option_b,
                "option_c": question.option_c,
                "option_d": question.option_d,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "question_type": question.question_type,
                "exam_date": question.exam_date.isoformat() if question.exam_date else None,
                "pyq_year": question.pyq_year,
                "shift": question.shift,
                "difficulty": question.difficulty,
            }
        )

    return render(
        request,
        "practice/practice_detail.html",
        {
            "subject": subject,
            "practice_number": practice_number,
            "question_payload": question_payload,
            "questions_json": question_payload,
            "total_questions": len(question_payload),
            "page_title": (
                f"UGC NET {subject.name} Practice Questions "
                f"- Practice {practice_number}"
            ),
            "page_description": (
                f"Practise {len(question_payload)} UGC NET Paper 1 "
                f"{subject.name} questions in Practice {practice_number}. "
                "Review your answers and explanations as you work through "
                "the session."
            ),
        },
    )
