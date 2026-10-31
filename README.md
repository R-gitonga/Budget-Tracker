# Budget Tracker

A multi-user personal finance web app built with **Flask**. Users register, log income and expenses, organise them into categories, set savings goals, and view charts summarising where their money goes. Amounts are in Kenyan shillings (Ksh).

> Status: dormant school project, being revived. This README documents what the code does **today**, including known problems (see [Known issues](#known-issues)).

---

## Features (current scope)

| Area | What works |
|------|------------|
| **Accounts** | Register, log in/out (Flask-Login, hashed passwords, "remember me") |
| **Transactions** | Add, edit, delete, list. Positive amount = income, negative = expense. Totals for income, expenses and balance |
| **Categories** | Per-user categories; add, rename, delete (deletion blocked if transactions use it). Quick-add from the transaction form via a modal |
| **Analytics** (`/analytics`, labelled "Summary" in the nav) | Chart.js charts: income vs expenses, spending by category (pie), net amount over time (line) |
| **Goals** | Create savings goals with target, current amount, deadline, status; progress % is computed. View a goal and delete it |
| **Landing page** | Marketing-style home page, plus a feedback form that posts to Formspree |
| **Security basics** | CSRF protection (Flask-WTF), every query filtered by `current_user` |

Not built yet: password reset, email, budgets/limits per category, recurring transactions, import/export, tests.

---

## Tech stack

- Python 3.10+ (developed on 3.13, verified on 3.12)
- Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF / WTForms, Flask-Migrate (Alembic)
- SQLite by default; PostgreSQL supported via `DATABASE_URL` (`psycopg2-binary`)
- Jinja2 templates, Bootstrap 5.3 and Chart.js (both loaded from the jsDelivr CDN, so an internet connection is needed for styling and charts)
- gunicorn + `Procfile` for deployment (Render/Heroku style)

---

## Project layout

```
Budget-Tracker/
├── run.py                # Entry point (app factory + shell context)
├── config.py             # Config: SECRET_KEY, DATABASE_URL (defaults to ./budget.db)
├── requirements.txt
├── reset_db.py           # Deletes all transactions and categories (not users/goals)
├── budget.db             # Default SQLite DB (schema present, no data)
├── instance/budget.db    # Older DB with test data (2 users, 7 transactions)
├── migrations/           # Alembic migrations (3 versions: initial, goals, goal current_amount)
└── app/
    ├── __init__.py       # create_app(), extensions
    ├── models.py         # User, Category, Transaction, Goal
    ├── forms.py          # WTForms definitions
    ├── routes.py         # Main blueprint: transactions, categories, analytics, goals
    ├── auth/routes.py    # /auth/register, /auth/login, /auth/logout
    ├── templates/        # Jinja2 templates (base.html is the layout)
    ├── static/           # css, js/chart.js, banner images
    ├── .env              # Old env file (NOT loaded automatically, see below)
    └── procfile          # web: gunicorn run:app
```

---

## Running it locally

### 1. Install Python

Install Python 3.10 or newer from <https://www.python.org/downloads/>. On Windows, tick **"Add python.exe to PATH"** in the installer. Check it worked:

```bash
python --version        # Windows (or: py --version)
python3 --version       # macOS / Linux
```

### 2. Get the code and create a virtual environment

From the project folder (`Budget-Tracker/`):

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt and `.venv\Scripts\activate.bat`.

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Recommended) Set a secret key

Without one the app falls back to the insecure default `dev-key`, which is fine on your own machine but not for anything shared.

**Windows (PowerShell)**
```powershell
$env:SECRET_KEY = "any-long-random-string"
```
**macOS / Linux**
```bash
export SECRET_KEY="any-long-random-string"
```

> The `app/.env` file in the repo is **not read** by the code (`config.py` never calls `load_dotenv`, and the file is in the wrong folder anyway). Set environment variables as above, or see [Known issues](#known-issues) to wire up `.env` properly.

### 5. Create or update the database

The bundled `budget.db` already has the right tables, so you can skip this on a first run. For a fresh or missing database, or after pulling new migrations:

```bash
flask --app run db upgrade
```

### 6. Start the app

```bash
flask --app run run --debug
```
or simply
```bash
python run.py
```

Open <http://127.0.0.1:5000>, click **Register**, create an account, then add a category (e.g. "Food") and your first transaction.

### Using the older database with test data

`instance/budget.db` holds data from the earlier version (2 users, 8 categories, 7 transactions, 2 goals). The app does not use it by default. To point the app at it, set `DATABASE_URL` to its **absolute** path before starting:

**Windows (PowerShell)**
```powershell
$env:DATABASE_URL = "sqlite:///C:/full/path/to/Budget-Tracker/instance/budget.db"
```
**macOS / Linux**
```bash
export DATABASE_URL="sqlite:////full/path/to/Budget-Tracker/instance/budget.db"
```
(Note three slashes on Windows paths, four on Unix paths.) I don't have the passwords for those accounts, so register a new user or reset the database if you can't log in.

### Using PostgreSQL

```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
flask --app run db upgrade
```
`postgres://` URLs (as supplied by Heroku/Render) are rewritten to `postgresql://` automatically.

---

## Common tasks

| Task | Command |
|------|---------|
| Change a model, then generate a migration | `flask --app run db migrate -m "describe change"` |
| Apply migrations | `flask --app run db upgrade` |
| Interactive shell with `db`, `User`, `Transaction`, `Category` loaded | `flask --app run shell` |
| Wipe all transactions and categories (keeps users and goals) | `python reset_db.py` |
| Run like production | `gunicorn run:app` (Linux/macOS; not available on Windows, use `waitress` there) |

---

## Known issues

Found while reviewing and smoke-testing the code. Roughly in order of how much they matter:

1. **Edit Goal is broken.** `edit_goal` in `app/routes.py` renders `goals/edit_goal.html`, which expects a WTForms `form` that the route never passes (500 error on GET). The POST path also assigns the deadline as a raw string (SQLite rejects it) and redirects to a non-existent endpoint `main.goal` (should be `main.goals`).
2. **`delete_goal` has no `@login_required`.** It is still scoped by user ID, but an anonymous request will crash on `current_user.id`.
3. **Category names are globally unique** (`unique=True` on `Category.name` in `models.py`), so two users cannot both have a "Food" category, although the "add category" modal route checks uniqueness per user. This needs a composite unique constraint (`user_id`, `name`) plus a migration.
4. **`.env` is never loaded**, and it is committed to git. Move it to the project root, call `load_dotenv()` in `config.py`, and keep it out of version control.
5. **Secrets and data committed to git:** `app/.env`, both `.db` files and `__pycache__/` folders are tracked. There is no `.gitignore`. Treat the `SECRET_KEY` in that `.env` as compromised and generate a new one. Because the repo history contains it, rotate it rather than just deleting the file.
6. **Template mismatch:** `app/templates/summary.html` is an empty file (the working page is `analytics.html`, linked as "Summary").
7. **Net-over-time chart** uses a 10% opacity line colour (`rgba(13,110,253,0.1)`), so the line is nearly invisible.
8. **Inconsistent line endings.** Git reports nearly every file as modified because of CRLF/LF differences. Adding a `.gitattributes` (`* text=auto`) will stop this.
9. **Deletes via GET:** transactions are deleted through a plain link (`GET`), which is unsafe (CSRF, prefetching). Switch to POST like categories and goals.
10. **Minor:** `datetime.utcnow` is deprecated in newer Python versions; `User.query.get` is deprecated in SQLAlchemy 2 (use `db.session.get`); registration form's submit button is labelled "Login"; `reset_db.py` does not delete goals; the debug `print('✅ Form Submitted')` in `add_goal` should go.

---

## Suggested roadmap

1. Housekeeping: add `.gitignore`, rotate the secret, remove tracked `.env`/`.db`/`__pycache__`, normalise line endings.
2. Fix the bugs above (especially goals editing and per-user category uniqueness).
3. Add tests (`pytest` with Flask's test client) covering auth, transactions and goals.
4. Features: category budgets, date-range filters, CSV export, recurring transactions.

---

## License

GNU GPL v3; see [LICENSE](LICENSE).