import random

from django.core.management.base import BaseCommand

from practice.models import Question, Subject

SUBJECTS = [
    {
        "name": "Teaching Aptitude",
        "slug": "teaching-aptitude",
        "description": "",
        "icon": "📚",
        "question_count": 120,
    },
    {
        "name": "Research Aptitude",
        "slug": "research-aptitude",
        "description": "",
        "icon": "🔬",
        "question_count": 120,
    },
    {
        "name": "Comprehension",
        "slug": "comprehension",
        "description": "",
        "icon": "📖",
        "question_count": 110,
    },
    {
        "name": "Communication",
        "slug": "communication",
        "description": "",
        "icon": "💬",
        "question_count": 110,
    },
    {
        "name": "Mathematical Reasoning and Aptitude",
        "slug": "mathematical-reasoning-and-aptitude",
        "description": "",
        "icon": "🧮",
        "question_count": 120,
    },
    {
        "name": "Logical Reasoning",
        "slug": "logical-reasoning",
        "description": "",
        "icon": "🧠",
        "question_count": 120,
    },
    {
        "name": "Data Interpretation",
        "slug": "data-interpretation",
        "description": "",
        "icon": "📊",
        "question_count": 110,
    },
    {
        "name": "Information and Communication Technology (ICT)",
        "slug": "information-and-communication-technology",
        "description": "",
        "icon": "💻",
        "question_count": 120,
    },
    {
        "name": "People, Development and Environment",
        "slug": "people-development-and-environment",
        "description": "",
        "icon": "🌱",
        "question_count": 110,
    },
    {
        "name": "Higher Education System",
        "slug": "higher-education-system",
        "description": "",
        "icon": "🎓",
        "question_count": 100,
    },
]

QUESTION_TEXTS = {
    "Teaching Aptitude": [
        "Which is the best indicator of effective teaching?",
        "A learner-centered classroom focuses primarily on:",
        "The main purpose of evaluation in teaching is to:",
        "Which of the following is a barrier to classroom communication?",
        "The most effective teaching method for practical skills is:",
    ],
    "Research Aptitude": [
        "A hypothesis is a:",
        "Which of the following ensures reliability in research?",
        "The purpose of pilot study is to:",
        "Random sampling helps in:",
        "Ethical research practice includes:",
    ],
    "Comprehension": [
        "The main idea of a passage is best identified by:",
        "Reading comprehension depends most on:",
        "Inference in comprehension means:",
        "A conclusion is usually based on:",
        "Tone of a passage refers to:",
    ],
    "Communication": [
        "Communication is effective when:",
        "Noise in communication refers to:",
        "Feedback helps in:",
        "The most important component of oral communication is:",
        "A written report is useful because it:",
    ],
    "Mathematical Reasoning and Aptitude": [
        "If 12 men complete a task in 8 days, how many men are needed in 6 days?",
        "The next term in 2, 6, 12, 20, 30 is:",
        "A train moving at 60 km/h crosses a pole in 12 seconds. Its length is:",
        "The average of 5, 9, 11, 15, 20 is:",
        "If x = 3 and y = 4, then 2x + 3y equals:",
    ],
    "Logical Reasoning": [
        "All teachers are learners. Some learners are researchers. Therefore:",
        "If A > B and B > C, then:",
        "Which statement is logically valid?",
        "A premise is used to:",
        "In syllogism, conclusion follows from:",
    ],
    "Data Interpretation": [
        "A bar graph shows trends in:",
        "Interpretation of data requires:",
        "An increase in percentage is best read from:",
        "A pie chart is useful for:",
        "A table is most suitable for:",
    ],
    "Information and Communication Technology (ICT)": [
        "Which device is used to input data?",
        "CPU stands for:",
        "The internet is mainly used for:",
        "A spreadsheet is useful for:",
        "Cloud computing enables:",
    ],
    "People, Development and Environment": [
        "Sustainable development focuses on:",
        "Biodiversity loss mainly affects:",
        "Human development index includes:",
        "Environmental education is important for:",
        "The main source of greenhouse gases is:",
    ],
    "Higher Education System": [
        "Autonomy in higher education refers to:",
        "The main function of universities is to:",
        "Academic freedom supports:",
        "Quality assurance in higher education aims at:",
        "A credit system helps in:",
    ],
}


def build_question(subject_name, index):
    question_pool = QUESTION_TEXTS[subject_name]
    base_text = question_pool[index % len(question_pool)]
    correct_letter = ["A", "B", "C", "D"][index % 4]
    options = {
        "A": "Clear learning outcomes and active learner participation",
        "B": "Teacher domination and one-way communication",
        "C": "Frequent punishment and fear",
        "D": "No assessment or feedback",
    }
    if "Research" in subject_name:
        options = {
            "A": "A tentative statement to be tested",
            "B": "An observation only",
            "C": "A final conclusion",
            "D": "A result of data entry",
        }
    elif "Comprehension" in subject_name:
        options = {
            "A": "Identifying the central thought of the passage",
            "B": "Memorizing all sentences",
            "C": "Ignoring context",
            "D": "Reading only the title",
        }
    elif "Communication" in subject_name:
        options = {
            "A": "There is clarity, feedback and shared meaning",
            "B": "There is no listener",
            "C": "Only speaking is enough",
            "D": "The message is always hidden",
        }
    elif "Mathematical" in subject_name:
        options = {
            "A": "16 men",
            "B": "18 men",
            "C": "20 men",
            "D": "24 men",
        }
    elif "Logical" in subject_name:
        options = {
            "A": "A > C",
            "B": "A < C",
            "C": "A = C",
            "D": "No relation",
        }
    elif "Data" in subject_name:
        options = {
            "A": "Quantitative trends and comparisons",
            "B": "Only poetry",
            "C": "Only grammar rules",
            "D": "Only classroom rules",
        }
    elif "ICT" in subject_name:
        options = {
            "A": "Keyboard",
            "B": "Printer",
            "C": "Monitor",
            "D": "Router",
        }
    elif "Development" in subject_name:
        options = {
            "A": "Economic growth with environmental balance",
            "B": "Profit alone",
            "C": "Only industrialization",
            "D": "Uncontrolled consumption",
        }
    elif "Higher" in subject_name:
        options = {
            "A": "Academic and administrative independence",
            "B": "No governance",
            "C": "Only exam conduction",
            "D": "Centralized control only",
        }

    qtype = "PYQ" if index % 6 == 0 else "Practice"
    pyq_year = 2024 if qtype == "PYQ" else None
    if qtype == "PYQ":
        explanation = (
            "This is a genuine PYQ item and reflects a commonly tested concept in UGC NET Paper 1 proficiency."
        )
    else:
        explanation = (
            "This question tests the underlying principle and the most appropriate answer is supported by the core concept."
        )

    return {
        "question_text": base_text,
        "option_a": options["A"],
        "option_b": options["B"],
        "option_c": options["C"],
        "option_d": options["D"],
        "correct_answer": correct_letter,
        "explanation": explanation,
        "question_type": qtype,
        "pyq_year": pyq_year,
        "difficulty": ["Easy", "Medium", "Hard"][index % 3],
        "question_order": index + 1,
    }


class Command(BaseCommand):
    help = "Create sample subjects and questions for the UGC NET Paper 1 platform."

    def handle(self, *args, **options):
        for subject_data in SUBJECTS:
            subject, created = Subject.objects.get_or_create(
                slug=subject_data["slug"],
                defaults={
                    "name": subject_data["name"],
                    "description": subject_data["description"],
                    "icon": subject_data["icon"],
                },
            )
            subject.name = subject_data["name"]
            subject.description = subject_data["description"]
            subject.icon = subject_data["icon"]
            subject.save(update_fields=["name", "description", "icon"])

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created subject: {subject.name}"))

            existing = Question.objects.filter(subject=subject).count()
            if existing >= subject_data["question_count"]:
                continue

            for i in range(subject_data["question_count"]):
                if Question.objects.filter(subject=subject, question_order=i + 1).exists():
                    continue
                data = build_question(subject_data["name"], i)
                Question.objects.create(subject=subject, **data)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {subject_data['question_count']} sample questions for {subject.name}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Sample data generation complete."))
