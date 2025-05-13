#!/bin/bash
# Script to set up Git hooks for Crowbank Intranet project

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Git hooks for Crowbank Intranet...${NC}"

# Check if .git directory exists
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: .git directory not found.${NC}"
    echo -e "${YELLOW}Please run this script from the root of the repository.${NC}"
    exit 1
fi

# Ensure hooks directory exists
mkdir -p .git/hooks

# Copy pre-commit hook
echo -e "${GREEN}Setting up pre-commit hook...${NC}"
cp -f .git/hooks/pre-commit .git/hooks/pre-commit.backup 2>/dev/null || true
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Pre-commit hook for Crowbank Intranet
# Checks for sensitive files and warns about large files

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for sensitive files
echo "Checking for potentially sensitive files..."

# Patterns to check (expand as needed)
SENSITIVE_PATTERNS=(
  "\.env$"
  "\.pem$"
  "config/yaml/secret\.yaml$"
  "password|secret|token|key|credential"
  "\.db$"
  "\.sqlite3$"
)

# Check staged files against patterns
SENSITIVE_FILES=()
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
  FILES=$(git diff --cached --name-only | grep -E "$pattern")
  if [ -n "$FILES" ]; then
    SENSITIVE_FILES+=("$FILES")
  fi
done

# If sensitive files found, prompt for confirmation
if [ ${#SENSITIVE_FILES[@]} -gt 0 ]; then
  echo -e "${RED}WARNING: Potentially sensitive files detected in commit:${NC}"
  printf '%s\n' "${SENSITIVE_FILES[@]}"
  echo
  echo -e "${YELLOW}These files may contain sensitive information that should not be committed.${NC}"
  echo -e "${YELLOW}Are you sure you want to commit these files? (y/n)${NC}"
  read confirm
  
  if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Commit aborted."
    exit 1
  fi
  
  echo -e "${YELLOW}Proceeding with commit despite sensitive files...${NC}"
fi

# Check for large files (greater than 5MB)
large_files=$(git diff --cached --name-only | xargs -I{} du -h {} 2>/dev/null | grep -E '^[0-9.]+M' | awk '$1 > 5.0 {print $2}')

if [ -n "$large_files" ]; then
  echo -e "${YELLOW}WARNING: Large files detected in commit:${NC}"
  echo "$large_files"
  echo
  echo -e "${YELLOW}Consider whether these files should be tracked differently or ignored.${NC}"
  echo -e "${YELLOW}Are you sure you want to commit these files? (y/n)${NC}"
  read confirm_large
  
  if [ "$confirm_large" != "y" ] && [ "$confirm_large" != "Y" ]; then
    echo "Commit aborted."
    exit 1
  fi
  
  echo -e "${YELLOW}Proceeding with commit of large files...${NC}"
fi

# All checks passed
exit 0
EOF

# Make the hook executable
chmod +x .git/hooks/pre-commit
echo -e "${GREEN}Pre-commit hook installed.${NC}"

# Create post-checkout hook to remind about branch switching
echo -e "${GREEN}Setting up post-checkout hook...${NC}"
cp -f .git/hooks/post-checkout .git/hooks/post-checkout.backup 2>/dev/null || true
cat > .git/hooks/post-checkout << 'EOF'
#!/bin/bash

# Post-checkout hook for Crowbank Intranet
# Reminds you about the Crowbank Git workflow when switching branches

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Only show message when switching branches, not when checking out files
if [ $3 -eq 1 ]; then
    CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
    echo -e "${YELLOW}Switched to branch: ${GREEN}$CURRENT_BRANCH${NC}"
    echo -e "${YELLOW}Remember the Crowbank Git workflow:${NC}"
    echo -e "- Feature work should be on a feature branch: ${GREEN}feature/your-feature${NC}"
    echo -e "- When switching machines, use: ${GREEN}./scripts/sync-machines.sh end${NC}"
    echo -e "- When starting on another machine, use: ${GREEN}./scripts/sync-machines.sh start${NC}"
    echo -e "- See the full Git policy at: ${GREEN}docs/git-policy.md${NC}"
fi

exit 0
EOF

# Make the hook executable
chmod +x .git/hooks/post-checkout
echo -e "${GREEN}Post-checkout hook installed.${NC}"

echo -e "${GREEN}Git hooks setup complete!${NC}"
echo -e "${YELLOW}These hooks help maintain the project's Git workflow.${NC}"
echo -e "${YELLOW}For more details, see docs/git-policy.md${NC}" 