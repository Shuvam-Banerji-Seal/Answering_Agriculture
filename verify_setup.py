#!/usr/bin/env python3
"""
Agriculture Bot Setup Verification Script
This script verifies that all components are properly installed and configured.
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log(message, color=Colors.BLUE):
    print(f"{color}[VERIFY]{Colors.END} {message}")

def success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")

def warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")

def check_python_version():
    """Check Python version compatibility"""
    log("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        error(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        success(f"{package_name}")
        return True
    except ImportError:
        error(f"{package_name}")
        return False

def check_command(command):
    """Check if a system command is available"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        success(f"{command}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run([command, "version"], capture_output=True, check=True)
            success(f"{command}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            error(f"{command}")
            return False

def check_ollama_model():
    """Check if Ollama and gemma3:1b model are available"""
    log("Checking Ollama and models...")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        if "gemma3:1b" in result.stdout:
            success("Ollama with gemma3:1b model")
            return True
        else:
            warning("Ollama installed but gemma3:1b model not found")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        error("Ollama not available")
        return False

def check_agri_bot_modules():
    """Check if agri_bot_searcher modules are available"""
    log("Checking Agriculture Bot modules...")
    
    # Add src directory to path
    project_root = Path(__file__).parent
    src_path = project_root / "agri_bot_searcher" / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    modules_to_check = [
        ("agriculture_chatbot", "Agriculture Chatbot"),
        ("web_ui", "Web UI"),
        ("voice_transcription", "Voice Transcription"),
        ("voice_web_ui", "Voice Web UI")
    ]
    
    results = []
    for module_name, display_name in modules_to_check:
        try:
            importlib.import_module(module_name)
            success(f"{display_name}")
            results.append(True)
        except ImportError as e:
            if "voice" in module_name.lower():
                warning(f"{display_name} - Voice features may not be available")
            else:
                error(f"{display_name} - {str(e)}")
            results.append(False)
    
    return results

def check_environment_setup():
    """Check environment configuration"""
    log("Checking environment setup...")
    
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        success("Environment file (.env) exists")
        return True
    else:
        warning("Environment file (.env) not found - using defaults")
        return False

def main():
    """Main verification function"""
    print(f"{Colors.BLUE}Agriculture Bot Setup Verification{Colors.END}")
    print("=" * 50)
    
    all_checks = []
    
    # Core system checks
    all_checks.append(check_python_version())
    
    # Essential packages
    log("Checking essential Python packages...")
    essential_packages = [
        ("flask", "Flask"),
        ("requests", "Requests"),
        ("duckduckgo_search", "DuckDuckGo Search")
    ]
    
    for package, display in essential_packages:
        all_checks.append(check_package(display, package))
    
    # Voice packages (optional)
    log("Checking voice processing packages...")
    voice_packages = [
        ("torch", "PyTorch"),
        ("torchaudio", "TorchAudio"),
        ("transformers", "Transformers")
    ]
    
    voice_available = True
    for package, display in voice_packages:
        if not check_package(display, package):
            voice_available = False
    
    # NeMo (optional)
    nemo_available = check_package("NeMo Toolkit", "nemo")
    
    # System commands
    log("Checking system commands...")
    all_checks.append(check_command("ollama"))
    
    # Ollama model
    all_checks.append(check_ollama_model())
    
    # Agriculture bot modules
    module_results = check_agri_bot_modules()
    all_checks.extend(module_results[:2])  # Only count core modules as required
    
    # Environment setup
    check_environment_setup()
    
    # Summary
    print(f"\n{Colors.BLUE}Verification Summary{Colors.END}")
    print("=" * 30)
    
    core_working = all_checks.count(True) >= len(all_checks) * 0.7
    
    if core_working:
        success("Core functionality is working")
    else:
        error("Core functionality has issues")
    
    if voice_available and nemo_available:
        success("Voice functionality is fully available")
    elif voice_available:
        warning("Voice functionality is partially available (missing NeMo)")
    else:
        warning("Voice functionality is not available")
    
    print(f"\n{Colors.BLUE}To start the application:{Colors.END}")
    print("./start_agri_bot.sh")
    print("\nOr manually:")
    print("source agri_bot_env/bin/activate")
    print("cd agri_bot_searcher")
    if voice_available:
        print("python3 src/voice_web_ui.py  # With voice support")
    print("python3 src/web_ui.py  # Text only")
    
    return 0 if core_working else 1

if __name__ == "__main__":
    sys.exit(main())
