#!/bin/bash
# Script for syncing work between machines
# Usage: ./scripts/sync-machines.sh [end|start]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current branch
current_branch=$(git branch --show-current)

if [ "$1" == "end" ] || [ "$1" == "e" ]; then
    # End of work session - save changes
    echo -e "${YELLOW}Preparing to sync before ending work on this machine...${NC}"
    
    # Check for changes
    if git status --porcelain | grep -q .; then
        echo -e "${GREEN}Changes detected.${NC}"
        
        # Stash any uncommitted changes if needed
        if git status --porcelain | grep -q '^[^?]'; then
            echo -e "${YELLOW}Uncommitted changes found.${NC}"
            
            # Ask to commit changes
            echo -e "${YELLOW}Do you want to commit these changes? (y/n)${NC}"
            read commit_changes
            
            if [ "$commit_changes" == "y" ] || [ "$commit_changes" == "Y" ]; then
                echo -e "${YELLOW}Enter commit message:${NC}"
                read commit_msg
                
                git add .
                git commit -m "$commit_msg"
                echo -e "${GREEN}Changes committed.${NC}"
            else
                echo -e "${YELLOW}Creating WIP commit...${NC}"
                git add .
                git commit -m "WIP: Work in progress on $(date +%Y-%m-%d)"
                echo -e "${GREEN}WIP commit created.${NC}"
            fi
        else
            # Only untracked files
            echo -e "${YELLOW}Only untracked files found.${NC}"
            echo -e "${YELLOW}Do you want to add and commit these files? (y/n)${NC}"
            read add_files
            
            if [ "$add_files" == "y" ] || [ "$add_files" == "Y" ]; then
                echo -e "${YELLOW}Enter commit message:${NC}"
                read commit_msg
                
                git add .
                git commit -m "$commit_msg"
                echo -e "${GREEN}Files added and committed.${NC}"
            fi
        fi
    else
        echo -e "${GREEN}No changes to commit.${NC}"
    fi
    
    # Push changes
    echo -e "${YELLOW}Pushing changes to remote repository...${NC}"
    git push origin $current_branch
    echo -e "${GREEN}Changes pushed to branch: $current_branch${NC}"
    
    echo -e "${GREEN}Work synchronized. You can now safely switch to another machine.${NC}"
    
elif [ "$1" == "start" ] || [ "$1" == "s" ]; then
    # Start of work session - get latest changes
    echo -e "${YELLOW}Starting work session, syncing latest changes...${NC}"
    
    # Fetch and pull
    git fetch origin
    git pull origin $current_branch
    
    echo -e "${GREEN}Synchronized latest changes from branch: $current_branch${NC}"
    echo -e "${GREEN}Ready to work!${NC}"
    
else
    echo -e "${RED}Invalid or missing parameter.${NC}"
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ${GREEN}./scripts/sync-machines.sh end${NC} - Sync before ending work on this machine"
    echo -e "  ${GREEN}./scripts/sync-machines.sh start${NC} - Sync when starting work on this machine"
    echo -e "  Shorthand: ${GREEN}./scripts/sync-machines.sh e${NC} or ${GREEN}./scripts/sync-machines.sh s${NC}"
fi 