# Pull Request Conflict Resolution Guide

## Scenario: Xaheli's Pull Request with Conflicts

When Xaheli sends a pull request with conflicts, follow these steps to keep your `.gitignore` while accepting her other changes.

### Method 1: Manual Resolution

1. **Fetch Xaheli's changes:**
   ```bash
   # If it's a branch on the same repo:
   git fetch origin xaheli-branch-name
   
   # If it's from a fork:
   git remote add xaheli https://github.com/xaheli/Answering_Agriculture.git
   git fetch xaheli
   ```

2. **Create a merge branch:**
   ```bash
   git checkout -b merge-xaheli-pr
   ```

3. **Merge and handle conflicts:**
   ```bash
   git merge origin/xaheli-branch-name
   # or: git merge xaheli/main
   ```

4. **Resolve conflicts strategically:**
   ```bash
   # For .gitignore - use YOUR version:
   git checkout --ours .gitignore
   
   # For all other files - use XAHELI's version:
   git checkout --theirs filename1.py
   git checkout --theirs filename2.py
   # ... repeat for each conflicted file
   ```

5. **Complete the merge:**
   ```bash
   git add .
   git commit -m "Merge: Accept Xaheli's changes, keep our .gitignore"
   ```

### Method 2: Automated Resolution

Use the provided script:

```bash
# Automatic resolution
./resolve_pr_conflicts.sh xaheli-branch-name

# Or with explicit auto flag
./resolve_pr_conflicts.sh --auto xaheli-branch-name
```

### Method 3: GitHub Web Interface

1. **In GitHub PR interface:**
   - Click "Resolve conflicts" button
   - For `.gitignore`: Delete Xaheli's version, keep yours
   - For other files: Delete your version, keep Xaheli's
   - Click "Mark as resolved" for each file
   - Click "Commit merge"

### Verification Steps

After resolving conflicts:

```bash
# Check the merge result
git log --oneline -5

# Verify our .gitignore is intact
git show HEAD:.gitignore

# Test the application
python3 verify_setup.py

# Push the resolved merge
git push origin merge-xaheli-pr
```

### Common Conflict Patterns

#### .gitignore Conflicts
```
<<<<<<< HEAD (Your version)
# Your .gitignore content
*.pyc
__pycache__/
.env
=======
# Xaheli's .gitignore content  
*.log
temp/
>>>>>>> xaheli-branch
```

**Resolution:** Keep the HEAD (your) version:
```bash
git checkout --ours .gitignore
```

#### Code File Conflicts
```
<<<<<<< HEAD (Your version)
def your_function():
    pass
=======
def xaheli_function():
    return "improved"
>>>>>>> xaheli-branch
```

**Resolution:** Keep Xaheli's version:
```bash
git checkout --theirs filename.py
```

### Troubleshooting

- **If merge fails:** `git merge --abort` and try again
- **To see conflicted files:** `git status` or `git diff --name-only --diff-filter=U`
- **To reset:** `git reset --hard HEAD` (loses uncommitted changes)

### Final Steps

1. **Test everything works:**
   ```bash
   ./start_agri_bot.sh  # Should start without errors
   ```

2. **Create final PR or merge to main:**
   ```bash
   git checkout main
   git merge merge-xaheli-pr
   git push origin main
   ```

This approach ensures you keep your carefully crafted `.gitignore` while accepting all of Xaheli's improvements to the codebase.
