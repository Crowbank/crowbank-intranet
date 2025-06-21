# Claude Code Instructions for Crowbank Intranet

This file provides context for Claude when working on the Crowbank Intranet project.

## Getting Started

Before making any changes, please read these essential documentation files:

1. **Project Overview**: Read `/docs/project-overview.md` for a comprehensive understanding of the project
2. **Project Roadmap**: Review `/docs/project-roadmap.md` for detailed development phases and current priorities
3. **Development Guidelines**: Check `/docs/development-guidelines.md` for coding standards and best practices
4. **Data Model Design**: See `/docs/data-model-design.md` for database patterns and naming conventions
5. **Configuration**: Review `/docs/configuration_management.md` for setup and config management
6. **Git Policy**: Read `/docs/git-policy.md` for version control practices

## Project Context

**Crowbank Intranet** is an internal management platform for Crowbank Kennels & Cattery. It's replacing legacy systems with a modern, modular, maintainable solution.

### Tech Stack
- **Backend**: Python, Flask, SQLAlchemy, PostgreSQL
- **Frontend**: Tailwind CSS, HTMX, Alpine.js, Jinja2
- **File Storage**: Cloudflare R2 (S3-compatible)
- **Database Migration**: Custom migration system from SQL Server to PostgreSQL

### Key Directories
- `app/` - Main application code (models, services, routes, templates)
- `migration/` - Database migration scripts and tools
- `legacy/` - Legacy system integration and frontend
- `docs/` - Project documentation and guidelines
- `tests/` - Test suites
- `migrations/` - Alembic database migrations

## Current Focus

The project is currently in **database migration phase**, moving data from a legacy SQL Server system to PostgreSQL. Key migration components:

- `migration/importer.py` - Main import logic with FK translation
- `migration/config.py` - Database connection configuration  
- `migration/lookup.py` - Legacy ID to new ID mapping system

### Migration Status
✅ **Completed**: Core business data (customers, pets, bookings, daily allocations)
🔄 **Next**: Financial data (invoices, charges, payments)

## Important Notes

1. **Always check migration status** before making changes to migration code
2. **Follow the established patterns** in existing migration logic
3. **Test migrations thoroughly** - data integrity is critical
4. **Use the lookup system** for FK translations between legacy and new IDs
5. **Respect the enum values** defined in the PostgreSQL schema

## Git Workflow Guidelines

**Commit Strategy**: When a logical set of changes appears to be complete (e.g., feature implementation, bug fix, documentation update, refactoring), **always suggest creating a commit** before starting unrelated tasks. This maintains clean project history and prevents work from being lost.

**Commit Timing Indicators**:
- Completed feature or functionality
- Documentation updates or reorganization
- Configuration changes
- Bug fixes or error corrections
- Before switching to different areas of the codebase
- When requested by the user

**Commit Process**: Use the established Git workflow with proper commit messages and co-authorship attribution as defined in the main instructions.

## Running Migrations

```bash
# Test connection
python -m migration.test_connection

# Import specific tables
python -m migration.importer --tables table_name

# Force reimport (truncates first)
python -m migration.importer --tables table_name --force
```

## Need Help?

- Check the relevant documentation files in `/docs/`
- Review existing migration patterns in `migration/importer.py`
- Look at the model definitions in `app/models/` for schema understanding
- Check enum definitions and constraints in migration files under `migrations/versions/`