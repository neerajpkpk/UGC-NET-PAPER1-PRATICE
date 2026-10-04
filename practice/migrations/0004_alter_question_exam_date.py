from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("practice", "0003_question_exam_date_alter_question_shift"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="exam_date",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
