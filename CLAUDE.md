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

**Branch Management Strategy**: Before making ANY file changes, **always verify the current branch is appropriate** for the task at hand. Use this branch organization system:

- `feature/` - User-facing features (booking system, customer management, payment processing, UI components)
- `dev/` - Development support (MCP servers, tooling, infrastructure, configuration, environment setup)
- `docs/` - Documentation (project docs, guides, architectural decisions)
- `ops/` - Operations and deployment (Docker, cloud deployment, CI/CD)
- **Integration branches** (main/develop) - For stable releases and cross-feature integration

**Branch Verification Process**:
1. **Check current branch** before starting any task
2. **Assess task category** and determine appropriate branch type
3. **If current branch doesn't match task category**:
   - Review existing branches with `git branch -a`
   - Either checkout appropriate existing branch OR create new branch with logical naming
   - Suggest branch strategy to user before proceeding
4. **Complete workflow**: When task is finished, suggest commits, pushes, and potential merges as appropriate

**Never proceed with file changes on an inappropriate branch.** This maintains clean project history and logical separation of work types.

## Running Migrations

```bash
# Test connection
python -m migration.test_connection

# Import specific tables
python -m migration.importer --tables table_name

# Force reimport (truncates first)
python -m migration.importer --tables table_name --force
```

## Legacy System Access

**Legacy Project Location**: `~/crowbank-flask`

The legacy system (old PetAdmin-based Flask application) is located in `/home/crowbank/crowbank-flask`. This contains:
- Original business logic and workflows
- Legacy database views and stored procedures
- Current production system architecture
- Business rules and validation logic
- User interface patterns and workflows

**FileSystem MCP Configuration**: The FileSystem MCP server is configured to access the entire `/home/crowbank` directory, providing access to both:
- `~/crowbank-intranet` (new system being developed)
- `~/crowbank-flask` (legacy system for reference)

**Legacy System Understanding**: When working on migration tasks, refer to the legacy system to understand:
- How business processes currently work
- Data relationships and constraints
- User workflows and interface patterns
- Business rules and validation logic
- Integration points and external dependencies

## MCP Server Configuration Status

**Post-Restart Setup Required**: After Claude Code restart, the following MCP servers will be available:

### Production-Ready MCP Servers
- **Neon PostgreSQL**: Cloud database operations
- **MSSQL**: Legacy database access (192.168.0.200\SQLEXPRESS)
- **GitHub**: Repository management and operations
- **FileSystem**: Full home directory access (`/home/crowbank`)
- **Docker**: Container management

### MCP Servers for Legacy System Installation
The following MCP servers should be installed on the legacy system (`~/crowbank-flask`):
- **GitHub MCP**: Repository management
- **FileSystem MCP**: File operations
- **Docker MCP**: Container management
- **Email/SMS MCP**: Customer communications (when implemented)
- **Calendar MCP**: Booking management (when implemented)

**Note**: Do NOT install Neon MCP on legacy system - it uses different database infrastructure.

## Need Help?

- Check the relevant documentation files in `/docs/`
- Review existing migration patterns in `migration/importer.py`
- Look at the model definitions in `app/models/` for schema understanding
- Check enum definitions and constraints in migration files under `migrations/versions/`
- **Reference legacy system** in `~/crowbank-flask` for business logic understanding