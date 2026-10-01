# UGC NET Paper 1 Practice Platform

A Django practice platform for UGC NET Paper 1. Subjects and questions are stored in the database. Practice sessions are generated from each subject's current question count; they are not manually created or hardcoded.

## Current Project Status

- Django 5.1 project with the `practice` app.
- Ten UGC NET Paper 1 subjects are present in the local database.
- At the last check (2026-10-02), the local SQLite database had two Data Interpretation questions and one Teaching Aptitude question. Other subjects had none. Local database contents are not included in Git; check the admin for current records.
- Temporary test questions used to verify table and explanation display were removed.
- Django's `manage.py check` passed after the latest changes.
- The admin link is hidden from the public navigation; the admin remains available directly at `/admin/`.

## Features Implemented

- Subject question totals are counted from the database.
- Practice sessions are generated in groups of 50 questions. A subject with 1-50 questions gets Practice 1, 51-100 adds Practice 2, and so on. The final practice contains only the remaining questions.
- Subject pages show the database total and generated practice ranges.
- The practice page shows one question at a time with A-D options, answer feedback, explanation, Previous, Skip, Next, finish, and retry behavior.
- Question tables and basic text formatting render in the question prompt. Tables scroll horizontally on narrow screens.
- Newlines and blank lines in plain-text explanations are preserved on the practice page.
- Long question and option text wraps within the page.

## Local Setup (Windows PowerShell)

From the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open the site at `http://127.0.0.1:8000/` and the admin at `http://127.0.0.1:8000/admin/`. If the virtual environment already exists, activate it and skip the first command. If PowerShell blocks activation, run the project's Python executable directly, for example `\.venv\Scripts\python.exe manage.py check`.

To verify the project after changes:

```powershell
python manage.py check
```

## Database Configuration

- Local development uses SQLite in `db.sqlite3` when `POSTGRES_DB_NAME` is not set.
- If `POSTGRES_DB_NAME` is set, Django uses PostgreSQL with the `POSTGRES_DB_USER`, `POSTGRES_DB_PASSWORD`, `POSTGRES_DB_HOST`, and `POSTGRES_DB_PORT` variables.
- `DJANGO_ALLOWED_HOSTS` is a comma-separated list of hostnames. The local default is `localhost,127.0.0.1`; set the production domain through the hosting provider's environment settings.
- The configured database is selected when Django starts. If expected questions are missing, first confirm which database configuration is active.
- PostgreSQL requires installing a compatible psycopg driver. `requirements.txt` includes Django and `python-dotenv`; the PostgreSQL driver entry is currently commented out.
- Keep real database passwords and `DJANGO_SECRET_KEY` in a local, untracked `.env`; do not commit secrets.

## Adding Real Questions

1. Sign in at `/admin/` and create a Subject first if the subject does not exist.
2. Open **Questions → Add** and select the subject.
3. Fill Question text, Option A-D, Correct answer, Explanation, Question type, Exam date, PYQ year, and Shift when applicable, Difficulty, and Question order.
4. Give questions sequential `question_order` values within a subject so the 50-question practice ranges appear in the intended order. Ties are ordered by database ID.
5. Save. The subject total and practice cards update from the database automatically.

Do **not** run `python manage.py seed_data` when preparing the clean real question bank. That command creates demo/sample questions. It is only for development scenarios where sample content is explicitly wanted.

### Tables in Questions

Paste a table into the **Question text** field as HTML. The UI safely renders a limited set of tags: paragraphs, line breaks, emphasis, lists, and tables (`table`, `thead`, `tbody`, `tr`, `th`, `td`). Table cells may use `colspan` and `rowspan`. Unsupported HTML tags and attributes are not retained by the browser renderer. The four answer choices still go into their separate option fields.

Example:

```html
<p>Study the table and answer the question.</p>
<table>
	<thead><tr><th>Year</th><th>Students</th></tr></thead>
	<tbody>
		<tr><td>2021</td><td>150</td></tr>
		<tr><td>2025</td><td>500</td></tr>
	</tbody>
</table>
```

For explanations, paste plain text. Newlines and blank lines are preserved; HTML is not required.

For PYQs, enter the exam date and year, then select First Shift or Second Shift in the admin. Date and shift are optional for questions where they are unknown or not applicable. The practice badge shows the date, year, and selected shift.

## Models and Main Files

- `practice/models.py`: Subject/Question schema and dynamic 50-question grouping.
- `practice/admin.py` and `practice/forms.py`: Django admin question and subject entry.
- `practice/views.py`: homepage, subject/practice pages, and question payload.
- `practice/templates/practice/`: shared layout and page templates.
- `practice/static/practice/app.js`: question rendering and practice interactions, including safe formatted prompt content.
- `practice/static/practice/styles.css`: responsive layout, question table, text wrapping, and explanation formatting.
- `ugcnet_practice/settings.py`: SQLite/PostgreSQL selection and Django settings.

## PDF Import Notes / Next Work

- The two PDFs currently in the workspace are for UGC NET December 2025, 31 December, Shift 1, Subject 058 Law. The answer-key PDF contains answer IDs, but the question-paper PDF extracted as a candidate response sheet with placeholder options `1, 2, 3, 4`; it does not contain usable question statements and options. They are not Paper 1 questions, so they have not been imported.
- For future PYQ imports, use a complete readable question paper and its matching final answer key. Extract/organize questions by Paper 1 subject, solve and explain each, compare against the key, flag uncertain or mismatching answers, then add verified records through admin. Do not invent missing question text/options from an answer key.
- The Data Interpretation table question entered for display checking should be checked in admin for its Question type, PYQ year, correct answer, and explanation before treating it as verified PYQ content.

## Design Notes

- Practice sessions are computed and are not stored in a separate session table.
- Questions are ordered by `question_order`, then `id`.
- Randomized practice, user accounts/progress, bulk import, and automatic PDF parsing are not implemented yet.

## GitHub Repository

The project folder should have its own Git repository; do not run Git commands from the parent `C:\Users\neera` repository. `.gitignore` excludes `.env`, SQLite databases, virtual environments, generated files, and PDFs. Review that file before adding any other local material.

Create an empty GitHub repository (do not initialize it with a README), then open a terminal in this project folder and run:

```powershell
git init
git branch -M main
git status --short
git add -A
git status --short
git commit -m "Initial UGC NET practice platform"
git remote add origin https://github.com/neerajpkpk/UGC-NET-PAPER1-PRATICE.git
git push -u origin main
```

Before committing, confirm the staged list does not contain `.env`, `db.sqlite3`, `.venv`, question PDFs, or other private data. If Git reports that `origin` already exists, use `git remote set-url origin <repository-url>` instead of adding it again. Never paste GitHub passwords or access tokens into chat or source files; authenticate with Git Credential Manager or GitHub's browser sign-in.
