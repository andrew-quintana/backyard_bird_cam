#!/bin/bash

# Remember the current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch is $CURRENT_BRANCH"

# Get a list of all local branches
BRANCHES=$(git branch | sed 's/^..//' | tr '\n' ' ')
echo "Found branches: $BRANCHES"

# Function to clean IP addresses in files
clean_branch() {
    local branch=$1
    echo "Cleaning branch: $branch"
    
    # Find files with IP addresses
    FILES=$(grep -l "192\.168\." --include="*.md" --include="*.sh" -r . || echo "")
    
    if [ -z "$FILES" ]; then
        echo "  No files with IP addresses found in $branch"
        return
    fi
    
    echo "  Found files with IP addresses:"
    for FILE in $FILES; do
        echo "    $FILE"
        # Replace IP addresses with placeholder
        sed -i '' 's/192\.168\.[0-9]\{1,3\}\.[0-9]\{1,3\}/{ip_address}/g' "$FILE"
    done
    
    # Check if there are changes to commit
    if ! git diff --quiet; then
        echo "  Committing changes in $branch"
        git add -A
        git commit -m "Remove exposed IP addresses from $branch"
    else
        echo "  No changes to commit in $branch"
    fi
}

# Process each branch
for BRANCH in $BRANCHES; do
    echo "======================================"
    echo "Switching to branch $BRANCH"
    git checkout $BRANCH
    
    # Check if there's a remote tracking branch
    REMOTE_BRANCH=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "")
    
    if [ -n "$REMOTE_BRANCH" ]; then
        echo "  Branch $BRANCH is tracking $REMOTE_BRANCH"
        echo "  Pulling latest changes"
        git pull
    fi
    
    # Clean the branch
    clean_branch $BRANCH
done

# Return to the original branch
echo "======================================"
echo "Returning to original branch $CURRENT_BRANCH"
git checkout $CURRENT_BRANCH

echo "======================================"
echo "All branches have been processed."
echo ""
echo "To push all changes to remote: git push --all origin"
echo "To push all branches with tags: git push --all origin && git push --tags origin" 