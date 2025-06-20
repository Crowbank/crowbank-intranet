# MCP (Model Context Protocol) Usage Guide

This document describes the available MCPs configured for the Crowbank Intranet project and how to use them effectively.

## Available MCPs

### 1. **PostgreSQL MCP** (`postgres`)
- **Purpose**: Direct access to the main PostgreSQL database
- **Connection**: `192.168.0.201:54320/crowbank`
- **Use Cases**:
  - Query migrated data to validate migration results
  - Execute database maintenance scripts
  - Generate reports and analytics
  - Debug data integrity issues

### 2. **SQL Server MCP** (`sqlserver`) 
- **Purpose**: Access to legacy SQL Server database
- **Connection**: `192.168.0.200\SQLEXPRESS/crowbank`
- **Use Cases**:
  - Query legacy data during migration process
  - Compare data between old and new systems
  - Extract specific datasets for migration
  - Validate business logic against historical data

### 3. **AWS MCP** (`aws`)
- **Purpose**: Manage Cloudflare R2 storage and AWS-compatible services
- **Endpoint**: Cloudflare R2 storage endpoint
- **Use Cases**:
  - Upload/manage pet documents and media files
  - Configure bucket policies and permissions
  - Monitor storage usage and costs
  - Backup and archival operations

### 4. **GitHub MCP** (`github`)
- **Purpose**: Repository management and development workflow
- **Use Cases**:
  - Manage pull requests and code reviews
  - Create releases and tags
  - Handle issue tracking and project management
  - Automate deployment workflows

### 5. **Filesystem MCP** (`filesystem`)
- **Purpose**: Advanced file operations within the project directory
- **Scope**: `/home/crowbank/crowbank-intranet`
- **Use Cases**:
  - Batch file operations during migration
  - Generate code templates and boilerplate
  - Process log files and reports
  - Manage configuration files

### 6. **Docker MCP** (`docker`)
- **Purpose**: Container management and development environment
- **Use Cases**:
  - Build and manage application containers
  - Handle database containers for testing
  - Manage development environment services
  - Streamline deployment processes

## Configuration Setup

### YAML-Based Configuration

All MCP credentials are managed through the project's YAML configuration system. Add your credentials to `config/yaml/secret.yaml`:

```yaml
# MCP (Model Context Protocol) Credentials
mcp:
  # AWS/Cloudflare R2 credentials for cloud storage MCP
  aws:
    access_key_id: "your_r2_access_key_id"
    secret_access_key: "your_r2_secret_access_key"
    endpoint_url: "https://4c5e823c2366476787d1b49d50d5d0a4.r2.cloudflarestorage.com"
    region: "auto"
  
  # GitHub integration credentials
  github:
    personal_access_token: "ghp_your_github_personal_access_token"
  
  # Database connection strings for MCP servers
  databases:
    postgresql: "postgresql://user:pass@host:port/db"
    sqlserver: "mssql://user:pass@host/db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"
```

### Setting Up Environment Variables

MCPs require environment variables, which can be set from your YAML config using the provided script:

```bash
# Generate .env.mcp file from secret.yaml
python scripts/setup_mcp_env.py --generate-env

# Source the environment variables
source .env.mcp
```

### Restart Requirements

**Yes, you need to restart Claude Code after:**
1. Adding new MCPs to the configuration
2. Changing MCP connection strings or credentials
3. Updating environment variables

**You do NOT need to restart for:**
- Regular code changes in your project
- YAML configuration changes (non-MCP related)
- File operations within existing MCP scope

## Migration Workflow Examples

### Comparing Data Between Systems
```sql
-- Query legacy system via SQL Server MCP
SELECT COUNT(*) as legacy_customers FROM dbo.customers;

-- Query new system via PostgreSQL MCP  
SELECT COUNT(*) as migrated_customers FROM customers;
```

### File Management During Migration
```bash
# Use Filesystem MCP to process migration logs
find migration/logs -name "*.log" -mtime -1

# Generate migration reports
python scripts/generate_migration_report.py
```

### Docker Development Environment
```bash
# Use Docker MCP to manage development containers
docker-compose up -d postgres
docker-compose logs migration-service
```

## Best Practices

### Security
- Never store credentials in the MCP configuration
- Use environment variables for sensitive information
- Regularly rotate access keys and tokens
- Limit MCP access to necessary directories and resources

### Development Workflow
- Use PostgreSQL MCP for current database operations
- Use SQL Server MCP for legacy data queries only
- Use Filesystem MCP for project-specific file operations
- Use GitHub MCP for repository management and CI/CD

### Migration Process
1. **Query legacy data** via SQL Server MCP
2. **Process and transform** using Filesystem MCP
3. **Import to PostgreSQL** via PostgreSQL MCP
4. **Validate results** by comparing both systems
5. **Store artifacts** in R2 via AWS MCP

## Troubleshooting

### Connection Issues
- Verify network connectivity to database servers
- Check firewall rules for SQL Server (port 1433)
- Validate PostgreSQL connection (port 54320)

### Authentication Problems
- Ensure environment variables are properly set
- Verify GitHub token has required permissions
- Check R2 access keys are active and have proper permissions

### Permission Errors
- Filesystem MCP is limited to project directory
- Docker MCP requires Docker daemon access
- AWS MCP requires proper IAM permissions for R2

## Integration with Migration Scripts

The MCPs integrate seamlessly with your existing migration infrastructure:

```python
# migration/importer.py can now leverage MCP connectivity
# for real-time validation and reporting
```

This setup provides comprehensive tooling for your database migration and ongoing development needs.