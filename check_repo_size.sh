#!/bin/bash

# Repository Size Monitor Script
# This script helps monitor the repository size and identify large files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Repository Size Monitor${NC}"
echo "==============================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Not in a git repository${NC}"
    exit 1
fi

# Repository information
echo -e "${GREEN}📊 Repository Information:${NC}"
echo "Repository: $(basename $(git rev-parse --show-toplevel))"
echo "Branch: $(git branch --show-current)"
echo "Remote: $(git remote get-url origin 2>/dev/null || echo 'No remote configured')"
echo ""

# Git repository size
echo -e "${GREEN}📦 Git Repository Size:${NC}"
git count-objects -vH
echo ""

# Large files in working directory (not tracked by git)
echo -e "${YELLOW}⚠️  Large Files in Working Directory (>10MB):${NC}"
large_files=$(find . -size +10M -not -path "./.git/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./env/*" 2>/dev/null)

if [ -z "$large_files" ]; then
    echo "✅ No large files found in working directory"
else
    echo "$large_files" | while read -r file; do
        size=$(du -h "$file" 2>/dev/null | cut -f1)
        ignored_status=""
        if git check-ignore "$file" >/dev/null 2>&1; then
            ignored_status="✅ (ignored)"
        else
            ignored_status="❌ (NOT IGNORED)"
        fi
        echo "  $size - $file $ignored_status"
    done
fi
echo ""

# Files tracked by git that are large
echo -e "${YELLOW}📋 Large Files Tracked by Git (>1MB):${NC}"
git ls-files | while read -r file; do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null || echo 0)
        if [ "$size" -gt 1048576 ]; then  # 1MB in bytes
            human_size=$(numfmt --to=iec-i --suffix=B "$size")
            echo "  $human_size - $file"
        fi
    fi
done | sort -hr | head -10

if [ ! -s /tmp/large_tracked_files.tmp ]; then
    echo "✅ No large files tracked by git"
fi
echo ""

# Check .gitignore effectiveness
echo -e "${GREEN}🛡️  .gitignore Effectiveness:${NC}"
echo "Testing common large file patterns..."

# Test patterns
test_patterns=(
    "*.jsonl"
    "*.tar.xz"
    "*.zip"
    "*.nemo"
    ".venv/"
    "__pycache__/"
    "models/"
    "*.log"
)

for pattern in "${test_patterns[@]}"; do
    # Create a temporary test file to check if it would be ignored
    test_file="/tmp/test_$RANDOM"
    touch "$test_file"
    mv "$test_file" "$pattern" 2>/dev/null || true
    
    if [ -f "$pattern" ]; then
        if git check-ignore "$pattern" >/dev/null 2>&1; then
            echo "  ✅ $pattern - properly ignored"
        else
            echo "  ❌ $pattern - NOT ignored"
        fi
        rm -f "$pattern"
    fi
done
echo ""

# Recommendations
echo -e "${BLUE}💡 Recommendations:${NC}"

# Check for common issues
issues_found=false

# Check if any large files are not ignored
large_unignored=$(find . -size +10M -not -path "./.git/*" -not -path "./.venv/*" 2>/dev/null | while read -r file; do
    if ! git check-ignore "$file" >/dev/null 2>&1; then
        echo "$file"
    fi
done)

if [ ! -z "$large_unignored" ]; then
    echo "⚠️  Large files found that are NOT ignored:"
    echo "$large_unignored" | sed 's/^/    /'
    echo "   Consider adding these patterns to .gitignore"
    issues_found=true
fi

# Check if .env files exist and are properly ignored
if find . -name ".env*" -not -path "./.git/*" | head -1 | grep -q .; then
    env_files_unignored=$(find . -name ".env*" -not -path "./.git/*" | while read -r file; do
        if ! git check-ignore "$file" >/dev/null 2>&1; then
            echo "$file"
        fi
    done)
    
    if [ ! -z "$env_files_unignored" ]; then
        echo "⚠️  Environment files that are NOT ignored:"
        echo "$env_files_unignored" | sed 's/^/    /'
        echo "   These may contain sensitive information!"
        issues_found=true
    fi
fi

# Check for Python cache files
if find . -name "__pycache__" -o -name "*.pyc" | head -1 | grep -q .; then
    cache_unignored=$(find . -name "__pycache__" -o -name "*.pyc" | while read -r file; do
        if ! git check-ignore "$file" >/dev/null 2>&1; then
            echo "$file"
        fi
    done)
    
    if [ ! -z "$cache_unignored" ]; then
        echo "⚠️  Python cache files that are NOT ignored:"
        echo "$cache_unignored" | head -5 | sed 's/^/    /'
        issues_found=true
    fi
fi

if [ "$issues_found" = false ]; then
    echo "✅ No issues found! Repository is well-configured."
fi

echo ""
echo -e "${GREEN}🔧 Maintenance Commands:${NC}"
echo "  Check large files: find . -size +10M -not -path './.git/*'"
echo "  Test .gitignore: git check-ignore <filename>"
echo "  Repository size: git count-objects -vH"
echo "  Clean untracked: git clean -f -d"
echo ""

echo -e "${GREEN}✨ Repository monitoring complete!${NC}"
