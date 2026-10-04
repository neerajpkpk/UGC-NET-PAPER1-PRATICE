import csv
from io import StringIO

from django.core.exceptions import ValidationError

from .models import Question

MAX_CSV_SIZE = 5 * 1024 * 1024
MAX_CSV_ROWS = 500

REQUIRED_COLUMNS = {
    "question_text",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_answer",
}
OPTIONAL_COLUMNS = {
    "subject",
    "subject_id",
    "question_order",
    "explanation",
    "question_type",
    "difficulty",
    "exam_date",
    "pyq_year",
    "shift",
}
CSV_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


class QuestionCSVImportError(Exception):
    pass


def parse_questions_csv(
    uploaded_file,
    subjects_by_name,
    subjects_by_id=None,
    *,
    selected_subject=None,
    starting_order=1,
):
    content = uploaded_file.read(MAX_CSV_SIZE + 1)
    if len(content) > MAX_CSV_SIZE:
        raise QuestionCSVImportError("CSV file must be 5 MB or smaller.")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise QuestionCSVImportError("CSV file must use UTF-8 encoding.") from error

    reader = csv.DictReader(StringIO(text), strict=True)
    if not reader.fieldnames:
        raise QuestionCSVImportError("CSV file is empty or missing its header row.")

    headers = [header.strip() if header else "" for header in reader.fieldnames]
    if len(headers) != len(set(headers)):
        raise QuestionCSVImportError("CSV contains duplicate column names.")

    subject_columns = {"subject", "subject_id"} & set(headers)
    if selected_subject is not None:
        if subject_columns or "question_order" in headers:
            raise QuestionCSVImportError(
                "When a subject is selected in the form, omit subject, "
                "subject_id, and question_order columns from the CSV."
            )
        if starting_order < 1:
            raise QuestionCSVImportError("Starting question order must be positive.")
    elif len(subject_columns) != 1:
        raise QuestionCSVImportError(
            "CSV must contain exactly one subject column: subject or subject_id."
        )

    missing_columns = REQUIRED_COLUMNS - set(headers)
    if selected_subject is None and "question_order" not in headers:
        missing_columns.add("question_order")
    if missing_columns:
        raise QuestionCSVImportError(
            "CSV is missing required columns: " + ", ".join(sorted(missing_columns))
        )

    unknown_columns = set(headers) - CSV_COLUMNS
    if unknown_columns:
        raise QuestionCSVImportError(
            "CSV contains unsupported columns: " + ", ".join(sorted(unknown_columns))
        )

    questions = []
    errors = []
    seen_orders = {}
    next_question_order = starting_order

    try:
        for row_number, raw_row in enumerate(reader, start=2):
            if row_number > MAX_CSV_ROWS + 1:
                raise QuestionCSVImportError(
                    f"CSV cannot contain more than {MAX_CSV_ROWS} question rows."
                )

            if None in raw_row:
                errors.append(f"Row {row_number}: contains more values than the header.")
                continue
            if any(value is None for value in raw_row.values()):
                errors.append(f"Row {row_number}: has missing values for one or more columns.")
                continue

            row = {
                key.strip(): value.strip()
                for key, value in raw_row.items()
                if key is not None
            }
            if not any(row.values()):
                continue

            if selected_subject is not None:
                subject = selected_subject
                question_order = next_question_order
                next_question_order += 1
            else:
                subject = None
            if selected_subject is None and "subject" in subject_columns:
                subject_name = row["subject"]
                subject = subjects_by_name.get(subject_name)
                subject_description = f"subject {subject_name!r}"
            elif selected_subject is None:
                subject_id = row["subject_id"]
                try:
                    subject = (subjects_by_id or {}).get(int(subject_id))
                except ValueError:
                    subject = None
                subject_description = f"subject_id {subject_id!r}"
            if subject is None:
                errors.append(
                    f"Row {row_number}: unknown {subject_description}; "
                    "use an existing subject from the admin."
                )
                continue

            subject_name = subject.name
            if selected_subject is None:
                try:
                    question_order = int(row["question_order"])
                except ValueError:
                    errors.append(f"Row {row_number}: question_order must be a whole number.")
                    continue

            duplicate_key = (subject.pk, question_order)
            if duplicate_key in seen_orders:
                errors.append(
                    f"Row {row_number}: question_order {question_order} for "
                    f"{subject_name} is also used in row {seen_orders[duplicate_key]}."
                )
                continue
            seen_orders[duplicate_key] = row_number

            try:
                pyq_year = int(row["pyq_year"]) if row.get("pyq_year") else None
            except ValueError:
                errors.append(f"Row {row_number}: pyq_year must be a whole number or blank.")
                continue

            question = Question(
                subject=subject,
                question_order=question_order,
                question_text=row["question_text"],
                option_a=row["option_a"],
                option_b=row["option_b"],
                option_c=row["option_c"],
                option_d=row["option_d"],
                correct_answer=row["correct_answer"].upper(),
                explanation=row.get("explanation", ""),
                question_type=row.get("question_type") or "Practice",
                difficulty=row.get("difficulty") or "Medium",
                exam_date=row.get("exam_date", ""),
                pyq_year=pyq_year,
                shift=row.get("shift", ""),
            )

            try:
                question.full_clean()
            except ValidationError as error:
                for field, messages in error.message_dict.items():
                    label = field.replace("_", " ")
                    errors.extend(
                        f"Row {row_number}: {label}: {message}"
                        for message in messages
                    )
                continue

            questions.append(question)
    except csv.Error as error:
        raise QuestionCSVImportError(f"Could not read CSV: {error}") from error

    if not questions and not errors:
        errors.append("CSV contains no question rows.")
    if errors:
        raise QuestionCSVImportError("\n".join(errors))

    return questions
