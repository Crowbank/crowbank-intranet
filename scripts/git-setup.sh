#!/bin/bash
# Git setup script for Crowbank Intranet project

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Git repository for Crowbank Intranet...${NC}"

# Check if git is already initialized
if [ -d ".git" ]; then
    echo -e "${YELLOW}Git repository already exists.${NC}"
else
    echo -e "${GREEN}Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}Git repository initialized.${NC}"
fi

# Check if remote origin exists
if git remote -v | grep -q origin; then
    echo -e "${YELLOW}Remote 'origin' already exists.${NC}"
else
    echo -e "${YELLOW}Please enter your GitHub repository URL:${NC}"
    read repo_url
    git remote add origin $repo_url
    echo -e "${GREEN}Remote 'origin' added.${NC}"
fi

# Ensure main branch exists
if git rev-parse --verify main >/dev/null 2>&1; then
    echo -e "${YELLOW}Main branch already exists.${NC}"
else
    # Create main branch
    echo -e "${GREEN}Creating main branch...${NC}"
    git checkout -b main
    echo -e "${GREEN}Main branch created.${NC}"
fi

# Create dev branch if it doesn't exist
if git rev-parse --verify dev >/dev/null 2>&1; then
    echo -e "${YELLOW}Dev branch already exists.${NC}"
else
    # Create dev branch
    echo -e "${GREEN}Creating dev branch...${NC}"
    git checkout -b dev
    echo -e "${GREEN}Dev branch created.${NC}"
fi

# Add .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo -e "${GREEN}Creating .gitignore file...${NC}"
    cat > .gitignore << 'EOL'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.env
.venv

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# Configuration secrets
config/yaml/secret.yaml
EOL
    echo -e "${GREEN}.gitignore file created.${NC}"
fi

# Initial commit if repository is empty
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    echo -e "${GREEN}Making initial commit...${NC}"
    git add .
    git commit -m "Initial commit"
    echo -e "${GREEN}Initial commit created.${NC}"
fi

echo -e "${GREEN}Git setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Push to GitHub: ${GREEN}git push -u origin main${NC}"
echo -e "2. Switch to dev branch: ${GREEN}git checkout dev${NC}"
echo -e "3. Push dev branch: ${GREEN}git push -u origin dev${NC}"
echo -e "\nRefer to docs/git-policy.md for workflow guidelines."

# Make the script executable
chmod +x scripts/git-setup.sh 