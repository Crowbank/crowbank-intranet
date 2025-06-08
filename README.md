# 🐾 Crowbank Intranet System

**Crowbank Intranet** is the internal management platform for Crowbank Kennels & Cattery. It replaces legacy systems with a modern, modular, and maintainable solution, designed to streamline bookings, pet care, staff scheduling, and customer communication.

---

## 🎯 Key Goals

- **Modular & Maintainable**: Clean structure, clearly defined components.
- **User-Friendly**: Clear, simple UI tailored for non-technical staff.
- **AI-Ready**: Structured to support future AI integrations (vet assistant, automated booking, social media captioning).
- **Cloud-Native**: Prepared for deployment via Docker to platforms like Render or Fly.io.

---

## ⚙️ Technology Stack

- **Backend**: Python 3.11+, Flask 3.x, SQLAlchemy 2.x, Alembic
- **Frontend**: Tailwind CSS, HTMX, Alpine.js, Jinja2 Templates
- **Database**: PostgreSQL (migration from MSSQL)
- **File Storage**: Cloudflare R2 (S3-compatible object storage)
- **Email**: HTML templates with Jinja2, sent via Flask-Mail
- **Reports**: Word `.docx` templates (Mail Merge via Python)
- **Development Tools**: Cursor IDE, WSL (Windows), Docker, pytest

---

## 📁 Project Structure

```
crowbank-intranet/
├── app/
│   ├── models/          # SQLAlchemy ORM models
│   ├── services/        # Business logic replacing stored procedures
│   ├── routes/          # Flask Blueprints: views, APIs, HTMX endpoints
│   ├── templates/       # HTML views, email, print templates
│   ├── utils/           # Common utilities (logging, file storage, security)
│   ├── integrations/    # Third-party services (Stripe, Gravity Forms, AI)
│   └── tasks/           # Background/scheduled tasks
├── config/              # Configuration files for different environments
├── tests/               # Unit and integration tests
├── migrations/          # Alembic migrations
├── static/              # CSS (Tailwind), JS (HTMX/Alpine)
├── .env                 # Environment configuration (not in git)
└── run.py               # Application runner script
```

---

## 🚀 Getting Started (Development)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/crowbank-intranet.git
cd crowbank-intranet
```

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure your environment

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Key settings to configure:
- `FLASK_ENV`: Use `dev` for development, `test` for testing, or `prod` for production
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, etc.: Database connection details
- `SECRET_KEY`: Generate a secure key for Flask sessions

### 4. Run the development server

```bash
# Basic run
python run.py

# With specific environment
python run.py --env dev

# With specific host/port
python run.py --host 127.0.0.1 --port 8000

# With debug mode
python run.py --debug
```

---

## ⚙️ Configuration System

The application uses a centralized configuration system with environment-specific settings:

- **Base Settings**: `config/default.py` contains common settings for all environments
- **Environment-Specific**: `config/dev.py`, `config/test.py`, and `config/prod.py` contain environment-specific overrides
- **Secrets**: Sensitive data is loaded from environment variables or `.env` file

### Using Configuration in Code

#### Within Flask Routes/Views:
```python
from flask import current_app

# Access config values
db_url = current_app.config["SQLALCHEMY_DATABASE_URI"]
page_size = current_app.config["ITEMS_PER_PAGE"]
```

#### In Standalone Scripts:
```python
from app.utils.config_loader import load_config

# Load config
config = load_config()
db_url = config["SQLALCHEMY_DATABASE_URI"]

# Or get a single value
from app.utils.config_loader import get_config_value
page_size = get_config_value("ITEMS_PER_PAGE", default=20)
```

For more details, see the [Configuration Management](docs/configuration_management.md) documentation.

---

## 📌 Planned Features

- 🗓 **Bookings & Scheduling**: Manage pet bookings, check-ins, availability.
- 📋 **Custom Reports**: Printable run cards, medication sheets, feeding charts.
- 📩 **Dynamic Emails**: Customizable email templates for customer communication.
- 📷 **File Management**: Cloud storage of photos and documents (vaccination cards).
- 🤖 **AI Integration**: Vet advice assistant, automated customer interactions.

---

## 📐 Development Practices

- **MCP-driven** (Cursor Multi-Context Prompts) for consistent development guidance.
- **Type-checked**: Comprehensive use of Python type hints and mypy.
- **Tested**: Unit and integration tests using pytest.
- **Modular**: Clear boundaries between routes, services, and data layers.
- **Git Workflow**: Structured branching strategy with automated sync tools (see [Git Policy](docs/git-policy.md)).

---

## 🛠 Deployment Strategy

- Containerized with Docker.
- Cloud deployment via Render.com, Fly.io, or similar services.
- Managed PostgreSQL DB and object storage (Cloudflare R2).

---

## 📄 License

Internal use only—not for public distribution.

## Docker Secrets Handling

- Secrets (database credentials, API keys, etc.) are stored in `config/yaml/secret.yaml` and **must not** be committed to version control.
- The Docker image does **not** copy secrets at build time. Instead, `docker-compose.yml` mounts `config/yaml/secret.yaml` into the container at `/app/config/yaml/secret.yaml` (read-only).
- Ensure `config/yaml/secret.yaml` exists on your host before running `docker-compose up`.
- `.dockerignore` includes `config/yaml/secret.yaml` to prevent accidental inclusion in images.
- The application reads secrets from the mounted file at runtime.
