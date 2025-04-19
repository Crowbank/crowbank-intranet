# Crowbank Intranet Project - Comprehensive Summary

## Project Motivation and Strategic Goals
- Replace legacy PetAdmin and MSSQL-based system.
- Create a modular, maintainable, cloud-ready intranet application for Crowbank Kennels & Cattery.
- Clear, user-friendly interfaces tailored for non-technical staff.
- Prepare infrastructure for future AI-driven functionalities, such as vet assistance, automated booking, and social media integration.

## Technology Stack
- **Backend:** Python 3.11+, Flask 3.x, SQLAlchemy 2.x, Alembic for database migrations
- **Frontend:** Tailwind CSS for styling, HTMX for server-driven interactivity, Alpine.js for client-side interactivity
- **Database:** PostgreSQL (replacing MSSQL)
- **Storage:** Cloudflare R2 (S3-compatible), moving away from local NAS storage
- **Reporting:** Microsoft Word MailMerge (via `docx-mailmerge`) for printable reports
- **Email:** HTML templates rendered with Jinja2, sent via Flask-Mail

## System Architecture
- Clearly modular directory structure with explicit separation of concerns:
  - `models/`: Data models using SQLAlchemy
  - `services/`: Business logic encapsulation, replacing stored procedures
  - `routes/`: Flask Blueprints and route handlers (thin routes)
  - `templates/`: HTML, email, and report templates
  - `integrations/`: External integrations (Stripe, Gravity Forms, AI services)
  - `tasks/`: Background scheduled tasks using APScheduler
  - `utils/`: Utility modules for logging, file handling, security

## Development and Deployment Environment
- **IDE & Workflow:** Cursor IDE configured clearly with WSL (Ubuntu) on Windows
- **Version Control:** Git with a remote repository hosted on GitHub
- **Dockerization:** Containerization strategy for local development and cloud deployment (Render.com, Fly.io)
- **Testing:** pytest for unit and integration testing; mypy for type checking; smoke tests for critical routes and functionality

## AI Integration Roadmap
- Production-grade AI agents powered by structured MCP-style prompts
- AI-driven vet consultation module to assist staff in identifying and managing pet health issues
- Automated social media caption generation for pet photos
- Customer-facing AI chatbot to handle bookings, inquiries, cancellations, and dynamic FAQ responses
- Automated backend tasks: analyzing vaccination records, pet documentation, new customer questionnaires for red flags

## File and Storage Strategy
- Transition from local NAS storage to Cloudflare R2 for robust, secure, and scalable cloud storage
- Clear workflows for staff file uploads (vaccination cards, pet photos) from various devices and operating systems
- Direct browser-accessible cloud storage for efficient, secure file handling

## User Interface and Experience
- A dashboard with clear visual hierarchy, modular components, and a progressive disclosure of information to prevent cognitive overload
- Staff-friendly UI employing Tailwind, HTMX, and Alpine.js for intuitive, responsive interactions
- Role-based customization of dashboard views and tools
- Streamlined workflows (staff scheduling, pet management, reporting) using clear and efficient interactive patterns (bucket zones, HTMX-driven toggles)

## Reporting and Communication
- Clear separation of email templates (HTML/Jinja2) and printable reports (Word-based mail merge)
- User-editable email templates supporting Jinja2 logic (loops, conditionals), with secure rendering via sandboxed environments
- Automated and user-initiated printing strategies transitioning clearly from local (Word-based) printing to front-end (browser-based) PDF/HTML printing post cloud migration

## Comprehensive Project Plan Outline
1. **Core Infrastructure:** Git, WSL, Docker setup, initial Flask and Tailwind scaffolding
2. **Database Migration:** MSSQL to PostgreSQL via Alembic, schema optimization
3. **Business Logic Layer:** Clearly defined models and services to replace stored procedures, comprehensive testing
4. **Interactive Frontend Components:** HTMX and Alpine.js-based interactions, role-based toolbars, customizable dashboards
5. **External Integrations:** Stripe, Gravity Forms, AI-driven backend tasks and customer interactions
6. **File Storage Transition:** NAS to Cloudflare R2, robust cloud file management
7. **Deployment Strategy:** Dockerized deployment to cloud services, comprehensive smoke testing post-deployment

## Cursor IDE Configuration
- `.cursorrules` clearly capturing project-specific guidelines and conventions for AI-driven development assistance
- Planned MCP (Multi-Context Prompts) clearly defined for specific workflows and tasks within Cursor IDE

## Archiving and Project Documentation
- Structured documentation clearly maintained within the project's `docs/canvases/` folder
- Git version control providing comprehensive, trackable project history

## Future Development Considerations
- Expanded AI capabilities clearly integrated as system matures
- Continuous enhancement of UX based on real-world usage and staff feedback
- Regular revisits to project structure and architecture ensuring clear, maintainable evolution