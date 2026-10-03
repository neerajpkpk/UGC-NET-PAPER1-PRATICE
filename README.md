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
- `dj-database-url` parses the connection URL; production (`DJANGO_DEBUG=False`) requires PostgreSQL SSL, including when the URL does not already specify `sslmode=require`.
- Use the Neon connection URL for local development and deployment. Keep it, its password, and `DJANGO_SECRET_KEY` in the untracked `.env` locally or in the hosting provider's secret environment variables. Never commit or share these values.
- Set `DJANGO_DEBUG=True` only for local development and `False` in deployment.
- `DJANGO_ALLOWED_HOSTS` is a comma-separated list. Locally it defaults to `localhost,127.0.0.1`; in deployment, set it to the Render service hostname and any custom domain.
- The PostgreSQL driver (`psycopg`) and `dj-database-url` are included in `requirements.txt`.

### Example local `.env`

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

## Deployment Status: Render with Neon

Neon remains the database; Render hosts the Django web application. The project includes Gunicorn as its production WSGI server and WhiteNoise for static files. `.python-version` pins Render to Python 3.13.4, which is compatible with the pinned Django 5.1 release; do not override it with Python 3.14. Do not use Django's development `runserver` as the production start command.

Create a Render **Web Service** connected to this GitHub repository and configure:

- **Build command:** `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
- **Start command:** `gunicorn ugcnet_practice.wsgi:application`

Add these environment variables in Render:

- `DATABASE_URL`: Neon PostgreSQL connection URL, entered as a secret environment variable.
- `DJANGO_SECRET_KEY`: a unique, private production secret.
- `DJANGO_DEBUG`: `False`.
- `DJANGO_ALLOWED_HOSTS`: the Render service hostname, such as `your-service.onrender.com`; include a custom domain if configured.

The build command applies Django migrations to Neon on each deployment; review and commit intended migrations before deploying. After deployment, verify the homepage and `/admin/`. Do not run `loaddata` unless intentionally restoring a fixture; it is not needed for a normal deployment.

## Search Engine Indexing and SEO

- `/robots.txt` allows public pages and points crawlers to `/sitemap.xml`; it disallows the admin and health-check paths.
- `/sitemap.xml` lists the homepage and subject/practice pages that currently have questions. Empty subject pages are marked `noindex` until question content is added.
- Public pages provide a canonical URL, a page-specific title and description, and Open Graph metadata. These changes help crawlers and link previews understand the pages; they do not guarantee rankings or indexing.
- For Google indexing, add the deployed HTTPS URL as a **URL-prefix property** in [Google Search Console](https://search.google.com/search-console/), verify ownership using its HTML-tag method, and submit `https://your-service.onrender.com/sitemap.xml`. Replace the example hostname with the live Render hostname. Use URL Inspection to request indexing for the homepage and populated subject pages.
- Search autocomplete checked on 2026-10-03 suggested phrases such as “UGC NET Paper 1 mock test”, “UGC NET Paper 1 practice questions”, “UGC NET Paper 1 practice test online”, “UGC NET Paper 1 mock test with answers free”, and subject-specific searches for teaching aptitude, research aptitude, and logical reasoning. These are qualitative suggestions, not measured search volumes or ranking forecasts. The app should only target claims such as free, Hindi, PDF, PYQ, or full mock test if that content or feature is actually available.
- Add original questions with correct answers and clear explanations before expecting subject pages to compete for search traffic. Track impressions and queries in Search Console, then prioritize topics where the site has useful, substantial content. No SEO change can guarantee Google indexing or recommendations by AI tools.

### Health Check and UptimeRobot

`/health/` returns the plain-text response `ok` without querying PostgreSQL. It is intended for uptime checks, so it does not validate database availability.

To monitor the Render service with UptimeRobot:

1. Sign in to UptimeRobot and choose **Add New Monitor**.
2. Choose **HTTP(s)** as the monitor type and give the monitor a name, such as `UGC NET website`.
3. Enter `https://your-service.onrender.com/health/`, replacing the hostname with the Render service hostname.
4. Set the monitoring interval to **5 minutes** (the free-plan interval).
5. Select an alert contact method, then save the monitor.
6. Check the monitor dashboard after its first check; the expected response is HTTP `200` with body `ok`.

This endpoint check can keep the Render web service receiving requests, but it does not access or wake Neon. Availability behavior can still depend on the hosting providers' free-plan policies.

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
- `ugcnet_practice/settings.py`: required PostgreSQL configuration, production security, and static-file settings.

## Design Notes

- Practice sessions are computed and are not stored in a separate session table.
- Questions are ordered by `question_order`, then `id`.
- Randomized practice, user accounts/progress, bulk import, and automatic PDF parsing are not implemented yet.

## GitHub Repository

`.gitignore` excludes `.env`, SQLite files, virtual environments, generated files, and PDFs. Before pushing changes, check `git status` and make sure `.env`, database credentials, local data, and private files are not staged. Never put secrets in source files or commit messages.
