import math

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

QUESTIONS_PER_PRACTICE = 10


class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=80, default="book-open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def practice_count(self):
        if not self.total_questions:
            return 0
        return math.ceil(self.total_questions / QUESTIONS_PER_PRACTICE)

    def get_questions_for_practice(self, practice_number):
        if practice_number < 1:
            return []

        ordered_questions = self.questions.order_by("question_order", "id")
        total_questions = ordered_questions.count()
        if total_questions == 0:
            return []

        practice_limit = math.ceil(total_questions / QUESTIONS_PER_PRACTICE)
        if practice_number > practice_limit:
            return []

        start = (practice_number - 1) * QUESTIONS_PER_PRACTICE
        end = start + QUESTIONS_PER_PRACTICE
        return list(ordered_questions[start:end])

    def get_practice_cards(self):
        cards = []
        total_questions = self.total_questions
        if total_questions == 0:
            return cards

        count = self.practice_count
        for number in range(1, count + 1):
            start = (number - 1) * QUESTIONS_PER_PRACTICE + 1
            end = min(number * QUESTIONS_PER_PRACTICE, total_questions)
            question_count = end - start + 1
            cards.append(
                {
                    "number": number,
                    "question_count": question_count,
                    "start": start,
                    "end": end,
                    "url": reverse("practice_detail", args=[self.slug, number]),
                }
            )
        return cards

    def __str__(self):
        return self.name


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ("PYQ", "PYQ"),
        ("Practice", "Practice"),
    ]

    DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    SHIFT_CHOICES = [
        ("First", "First Shift"),
        ("Second", "Second Shift"),
    ]

    subject = models.ForeignKey(Subject, related_name="questions", on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])
    explanation = models.TextField(blank=True)
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPE_CHOICES, default="PYQ")
    exam_date = models.CharField(max_length=50, null=True, blank=True)
    pyq_year = models.PositiveIntegerField(null=True, blank=True)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="Medium")
    question_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["question_order", "id"]

    def __str__(self):
        return f"{self.subject.name} - Q{self.question_order}"
