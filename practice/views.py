from pathlib import Path

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Subject

BING_SITE_AUTH_FILE = Path(__file__).with_name("BingSiteAuth.xml")


SUBJECT_INTROS = {
    "teaching-aptitude": "Revise teaching methods, learner characteristics, teaching aids and classroom evaluation through previous year questions.",
    "research-aptitude": "Review research methods, sampling, data collection, research ethics and the fundamentals of academic writing.",
    "comprehension": "Build reading accuracy with passage-based questions that test understanding, inference and interpretation.",
    "communication": "Study communication models, classroom communication, barriers, media and the role of communication in learning.",
    "mathematical-reasoning-and-aptitude": "Practise number systems, arithmetic, ratios, percentages, series and quantitative reasoning.",
    "logical-reasoning": "Review arguments, fallacies, analogies, syllogisms, Indian logic and methods of reasoning.",
    "data-interpretation": "Practise reading tables, charts and graphs, then solve questions using comparison and quantitative analysis.",
    "information-and-communication-technology": "Review computer fundamentals, the internet, digital learning, communication technologies and ICT in education.",
    "people-development-and-environment": "Study environment, ecosystems, pollution, sustainable development, population and related policies.",
    "higher-education-system": "Review the development, governance, policies, institutions and changing landscape of higher education in India.",
}


def health(request):
    return HttpResponse("ok")


def bing_site_auth(request):
    return HttpResponse(
        BING_SITE_AUTH_FILE.read_bytes(),
        content_type="application/xml; charset=utf-8",
    )


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
    total_site_questions = sum(subject.total_questions for subject in subjects)
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
            "total_site_questions": total_site_questions,
            "page_title": "Free UGC NET Paper 1 PYQs | Subject-wise Previous Year Questions",
            "page_description": (
                "Practise UGC NET Paper 1 previous year questions across all "
                "10 units. Choose a subject, check answers and review explanations."
            ),
        },
    )


def subject_detail(request, slug):
    subject = Subject.objects.filter(slug=slug).first()
    if not subject:
        raise Http404("Subject does not exist.")

    practice_cards = subject.get_practice_cards()
    total_questions = subject.total_questions
    subject_intro = (getattr(subject, "description", "") or "").strip() or SUBJECT_INTROS.get(
        subject.slug,
        f"Explore UGC NET Paper 1 previous year questions for {subject.name} and review answers with explanations.",
    )
    page_title = f"UGC NET {subject.name} PYQs | Paper 1 Previous Year Questions"
    page_description = (
        f"Practise {total_questions} UGC NET Paper 1 {subject.name} PYQs. "
        f"{subject_intro}"
    )

    return render(
        request,
        "practice/subject_detail.html",
        {
            "subject": subject,
            "practice_cards": practice_cards,
            "total_questions": total_questions,
            "subject_intro": subject_intro,
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
                "exam_date": question.exam_date,
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
                f"UGC NET {subject.name} PYQ Set {practice_number} | Paper 1"
            ),
            "page_description": (
                f"Attempt {len(question_payload)} {subject.name} previous year "
                f"questions for UGC NET Paper 1. Check answers and explanations "
                f"in PYQ Set {practice_number}."
            ),
        },
    )
