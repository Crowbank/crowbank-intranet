# Git & GitHub Policy for Crowbank Intranet

This document outlines the Git and GitHub workflow for the Crowbank Intranet project.

## Repository Structure

- **Main Repository**: https://github.com/Crowbank/crowbank-intranet
- **Primary Branch**: `main` - Always contains production-ready code
- **Development Branch**: `dev` - Integration branch for features before merging to main

## Branching Strategy

As a sole developer working across multiple machines, we'll use a simplified Git Flow approach:

1. **Feature Branches**: `feature/descriptive-name` - For new features
2. **Bugfix Branches**: `bugfix/issue-description` - For bug fixes
3. **Hotfix Branches**: `hotfix/critical-fix` - For urgent production fixes

## Workflow for Daily Development

### Starting Work on a New Feature

```bash
# Ensure you're on dev and up-to-date
git checkout dev
git pull origin dev

# Create a feature branch
git checkout -b feature/your-feature-name

# Work on your feature with regular commits...

# When ready to integrate
git checkout dev
git pull origin dev  # Get any changes that might have happened
git merge feature/your-feature-name
git push origin dev

# Optional: Delete the feature branch when no longer needed
git branch -d feature/your-feature-name
```

### Synchronizing Between Machines

Always push your changes to GitHub before switching machines:

```bash
# Before ending work on one machine
git add .
git commit -m "WIP: Meaningful description of current state"
git push origin your-current-branch

# When starting on another machine
git pull origin your-current-branch
```

## Commit Guidelines

- **Commit Messages**: Use clear, descriptive commit messages
  - Format: `[Area]: Brief description of change`
  - Example: `[Customer Model]: Add validation for email fields`

- **Commit Frequency**: Commit logical units of work
  - Small, focused commits are preferred over large, monolithic changes
  - If a feature is partially complete when switching machines, use `WIP:` prefix

## Deployment Process

1. When the `dev` branch is stable and tested:
   ```bash
   git checkout main
   git merge dev
   git push origin main
   ```

2. Tag significant releases:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```

## Configuration & Secrets

- Store secrets in `.env` files (already in `.gitignore`)
- Configuration templates should be versioned (with placeholders)
- Actual configs with sensitive data should not be committed

## Database Migrations

- Always commit database migrations to version control
- Test migrations locally before pushing to GitHub

## Backup Strategy

- GitHub serves as the primary backup for code
- Regularly push work-in-progress to remote branches
- Consider scheduled database backups separate from Git

## Future Considerations for Team Development

- Pull Request workflow
- Code review process
- CI/CD integration
- Branch protection rules

## References

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/) 