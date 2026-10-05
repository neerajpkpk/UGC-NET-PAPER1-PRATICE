from django.db import migrations, models


def mark_existing_questions_as_pyq(apps, schema_editor):
    Question = apps.get_model("practice", "Question")
    Question.objects.filter(question_type="Practice").update(question_type="PYQ")


class Migration(migrations.Migration):

    dependencies = [
        ("practice", "0004_alter_question_exam_date"),
    ]

    operations = [
        migrations.RunPython(mark_existing_questions_as_pyq, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="question",
            name="question_type",
            field=models.CharField(
                choices=[("PYQ", "PYQ"), ("Practice", "Practice")],
                default="PYQ",
                max_length=15,
            ),
        ),
    ]
