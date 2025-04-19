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
├── tests/               # Unit and integration tests
├── migrations/          # Alembic migrations
├── static/              # CSS (Tailwind), JS (HTMX/Alpine)
├── .env                 # Environment configuration
└── Dockerfile           # Docker build config
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

Create a `.env` file:

```env
FLASK_ENV=development
DATABASE_URL=postgresql://localhost/crowbank_dev
SECRET_KEY=your-secret-key
```

### 4. Run the development server

```bash
flask run
```

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

---

## 🛠 Deployment Strategy

- Containerized with Docker.
- Cloud deployment via Render.com, Fly.io, or similar services.
- Managed PostgreSQL DB and object storage (Cloudflare R2).

---

## 📄 License

Internal use only—not for public distribution.
