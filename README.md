# UGC NET Paper 1 Practice Platform

A Django practice platform for UGC NET Paper 1. Subjects and questions are stored in the database. Practice sessions are generated from each subject's current question count; they are not manually created or hardcoded.

## Current Project Status

- Django 5.1 project with the `practice` app.
- The app requires PostgreSQL configured by `DATABASE_URL`; there is no SQLite fallback.
- The local `.env` is private and is not part of the repository. Each developer or deployment environment must supply its own configuration.
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
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Edit .env and set DATABASE_URL to the Neon connection URL.
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

If the virtual environment already exists, skip its creation. These commands use its Python directly, so activation is not required.

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Open the site at `http://127.0.0.1:8000/` and the admin at `http://127.0.0.1:8000/admin/`.

## Database Configuration

- `DATABASE_URL` must be a PostgreSQL connection URL. The app stops with a configuration error if it is missing or invalid; it does not create or fall back to a local SQLite database.
- Use the Neon connection URL for local development and deployment. Keep it, its password, and `DJANGO_SECRET_KEY` in the untracked `.env` locally or in the hosting provider's secret environment variables. Never commit or share these values.
- Set `DJANGO_DEBUG=True` only for local development and `False` in deployment.
- `DJANGO_ALLOWED_HOSTS` is a comma-separated list. Locally it defaults to `localhost,127.0.0.1`; in deployment, set it to the Render service hostname and any custom domain.
- The PostgreSQL driver (`psycopg`) is included in `requirements.txt`.

### Example local `.env`

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

## Deployment Status: Render with Neon

Neon remains the database; Render would host the Django web application. This repository is **not yet ready for a production Render deployment**: it does not include a production WSGI server such as Gunicorn or production static-file serving/configuration. Do not use Django's development `runserver` as the production start command.

Before deploying, add and verify the production server and static-file configuration. Then create a Render **Web Service** connected to this GitHub repository, set its build and start commands to match the configured production setup, and add these environment variables in Render:

- `DATABASE_URL`: Neon PostgreSQL connection URL, entered as a secret environment variable.
- `DJANGO_SECRET_KEY`: a unique, private production secret.
- `DJANGO_DEBUG`: `False`.
- `DJANGO_ALLOWED_HOSTS`: the Render service hostname, such as `your-service.onrender.com`; include a custom domain if configured.

After deployment, verify the homepage and `/admin/`. Apply database migrations to Neon only after reviewing the migration plan. Do not run `loaddata` unless intentionally restoring a fixture; it is not needed for a normal deployment.

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
- `ugcnet_practice/settings.py`: required PostgreSQL configuration and Django settings.

## Design Notes

- Practice sessions are computed and are not stored in a separate session table.
- Questions are ordered by `question_order`, then `id`.
- Randomized practice, user accounts/progress, bulk import, and automatic PDF parsing are not implemented yet.

## GitHub Repository

`.gitignore` excludes `.env`, SQLite files, virtual environments, generated files, and PDFs. Before pushing changes, check `git status` and make sure `.env`, database credentials, local data, and private files are not staged. Never put secrets in source files or commit messages.
