#!/bin/bash

# Script to handle pull request merge conflicts
# This script helps resolve conflicts favoring our .gitignore but accepting Xaheli's other changes

echo "🔀 Pull Request Conflict Resolution Helper"
echo "========================================="
echo

# Function to handle merge conflicts
handle_conflicts() {
    echo "📋 Steps to resolve merge conflicts with Xaheli's PR:"
    echo
    echo "1. First, fetch Xaheli's branch:"
    echo "   git fetch origin <xaheli-branch-name>"
    echo "   # or if it's a fork:"
    echo "   git remote add xaheli <xaheli-fork-url>"
    echo "   git fetch xaheli"
    echo
    echo "2. Create a new branch for the merge:"
    echo "   git checkout -b merge-xaheli-changes"
    echo
    echo "3. Attempt the merge:"
    echo "   git merge <xaheli-branch-name>"
    echo "   # This will show conflicts"
    echo
    echo "4. For .gitignore conflicts - use our version:"
    echo "   git checkout --ours .gitignore"
    echo
    echo "5. For all other conflicts - use Xaheli's version:"
    echo "   # List conflicted files:"
    echo "   git status --porcelain | grep '^UU'"
    echo "   # For each file (except .gitignore):"
    echo "   git checkout --theirs <filename>"
    echo
    echo "6. Commit the merge:"
    echo "   git add ."
    echo "   git commit -m 'Merge: Accept Xaheli changes, keep our .gitignore'"
    echo
    echo "7. Push and create PR or merge to main:"
    echo "   git push origin merge-xaheli-changes"
}

# Function to automatically resolve conflicts if they exist
auto_resolve_conflicts() {
    local xaheli_branch=$1
    
    if [ -z "$xaheli_branch" ]; then
        echo "❌ Please provide Xaheli's branch name"
        echo "Usage: $0 <xaheli-branch-name>"
        exit 1
    fi
    
    echo "🔄 Auto-resolving conflicts with branch: $xaheli_branch"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ Not in a git repository"
        exit 1
    fi
    
    # Create merge branch
    git checkout -b "merge-xaheli-$(date +%Y%m%d-%H%M%S)"
    
    # Attempt merge
    echo "🔀 Attempting merge..."
    if git merge "$xaheli_branch"; then
        echo "✅ Merge completed without conflicts"
        return 0
    fi
    
    echo "⚠️  Conflicts detected. Resolving..."
    
    # Get list of conflicted files
    conflicted_files=$(git diff --name-only --diff-filter=U)
    
    if [ -z "$conflicted_files" ]; then
        echo "✅ No conflicts to resolve"
        return 0
    fi
    
    echo "📁 Conflicted files:"
    echo "$conflicted_files"
    echo
    
    # Resolve each conflict
    for file in $conflicted_files; do
        if [ "$file" = ".gitignore" ]; then
            echo "🛡️  Keeping our .gitignore version for: $file"
            git checkout --ours "$file"
        else
            echo "📝 Using Xaheli's version for: $file"
            git checkout --theirs "$file"
        fi
        git add "$file"
    done
    
    # Commit the merge
    echo "💾 Committing merge resolution..."
    git commit -m "Merge: Accept Xaheli's changes, preserve our .gitignore

- Used Xaheli's version for all files except .gitignore
- Kept our .gitignore to maintain project structure
- Resolved conflicts automatically"
    
    echo "✅ Merge conflicts resolved!"
    echo "📋 Next steps:"
    echo "   - Review the changes: git log --oneline -5"
    echo "   - Test the application: ./verify_setup.py"
    echo "   - Push to remote: git push origin \$(git branch --show-current)"
}

# Main execution
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    handle_conflicts
elif [ "$1" = "--auto" ] && [ -n "$2" ]; then
    auto_resolve_conflicts "$2"
elif [ -n "$1" ]; then
    auto_resolve_conflicts "$1"
else
    handle_conflicts
fi
