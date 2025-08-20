# Dynamic Path Configuration - Improvements Summary

## Issue Fixed
Removed hardcoded user-specific paths from installation and startup scripts to make them portable across different systems and users.

## Changes Made

### 1. `install_agri_bot.sh`
**Before:**
```bash
PROJECT_ROOT="/home/shuvam/codes/Answering_Agriculture"
```

**After:**
```bash
# Get the directory where this script is located (works regardless of where it's run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
```

### 2. `start_agri_bot.sh`
**Before:**
```bash
PROJECT_ROOT="/home/shuvam/codes/Answering_Agriculture"
```

**After:**
```bash
# Get the directory where this script is located (works regardless of where it's run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
```

### 3. Generated startup script in `install_agri_bot.sh`
Fixed the embedded startup script generation to use dynamic paths as well.

## Benefits

✅ **Portable**: Scripts work regardless of where the project is located
✅ **User-agnostic**: No hardcoded usernames or home directories
✅ **Flexible**: Works in any directory structure
✅ **Maintainable**: No need to update paths when moving the project

## How It Works

The dynamic path detection uses:
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

This command:
1. `${BASH_SOURCE[0]}` - Gets the path of the current script
2. `dirname` - Gets the directory containing the script
3. `cd` + `pwd` - Resolves to absolute path, handling symlinks properly

## Testing

Users can now:
- Clone the repository to any location
- Run the scripts from any directory
- Move the project folder without breaking the scripts

Example usage:
```bash
# Works from any location
git clone https://github.com/Shuvam-Banerji-Seal/Answering_Agriculture.git /opt/agri-bot/
cd /opt/agri-bot/
./install_agri_bot.sh

# Or from user home
git clone https://github.com/Shuvam-Banerji-Seal/Answering_Agriculture.git ~/projects/agri-bot
cd ~/projects/agri-bot
./install_agri_bot.sh
```

Both scenarios will work correctly with the dynamic path detection.
