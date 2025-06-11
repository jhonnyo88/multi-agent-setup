"""
DigiNativa AI-Team: Environment Management
=========================================

PURPOSE: Environment-specific configuration and validation

MODULAR DESIGN:
- Validates required environment variables
- Provides environment-specific defaults
- Handles secure credential management

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update REQUIRED_VARIABLES for your services
2. Modify OPTIONAL_VARIABLES for your integrations  
3. Adjust validation logic for your requirements

VERSION: 1.0.0
CREATED: 2025-06-10
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from .base_config import settings

# 🔧 ADAPT: Required environment variables for your project
REQUIRED_VARIABLES = {
    "development": [
        "ANTHROPIC_API_KEY",  # 🔧 CHANGE: Your required AI service
        "GITHUB_TOKEN",       # 🔧 CHANGE: If using different version control
    ],
    "staging": [
        "ANTHROPIC_API_KEY",
        "GITHUB_TOKEN", 
        "DATABASE_URL",
    ],
    "production": [
        "ANTHROPIC_API_KEY",
        "GITHUB_TOKEN",
        "DATABASE_URL",
        "SENTRY_DSN",  # 🔧 ADD: Your monitoring service
    ]
}

# 🔧 ADAPT: Optional variables that enhance functionality
OPTIONAL_VARIABLES = [
    "OPENAI_API_KEY",      # 🔧 CHANGE: Your optional AI services
    "NETLIFY_TOKEN",       # 🔧 CHANGE: Your deployment service
    "SLACK_WEBHOOK_URL",   # 🔧 ADD: Your notification services
]

def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        Tuple of (is_valid, missing_variables)
    """
    current_env = settings.environment
    required_vars = REQUIRED_VARIABLES.get(current_env, [])
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def check_optional_variables() -> Dict[str, bool]:
    """
    Check which optional variables are available.
    
    Returns:
        Dictionary mapping variable names to availability
    """
    return {var: bool(os.getenv(var)) for var in OPTIONAL_VARIABLES}

def get_environment_info() -> Dict[str, any]:
    """
    Get comprehensive environment information for debugging.
    """
    is_valid, missing = validate_environment()
    optional = check_optional_variables()
    
    return {
        "environment": settings.environment,
        "is_valid": is_valid,
        "missing_required": missing,
        "optional_available": optional,
        "project_root": str(settings.project_root_path),
        "python_version": sys.version,
        "config_loaded": True
    }

def ensure_directories():
    """
    Ensure all required directories exist.
    """
    required_dirs = [
        settings.logs_directory,
        settings.specs_directory,
        settings.project_root_path / "reports" / "output",
        settings.project_root_path / "data" / "agent_state",
    ]
    
    for dir_path in required_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

def initialize_environment():
    """
    Initialize environment - call this at startup.
    
    Raises:
        EnvironmentError: If required variables are missing
    """
    # Ensure directories exist
    ensure_directories()
    
    # Validate environment
    is_valid, missing = validate_environment()
    
    if not is_valid:
        error_msg = f"""
        Missing required environment variables for {settings.environment}:
        {', '.join(missing)}
        
        Please check your .env file or environment configuration.
        See .env.template for required variables.
        """
        raise EnvironmentError(error_msg)
    
    # Log environment status (but not sensitive data)
    optional = check_optional_variables()
    print(f"✅ Environment '{settings.environment}' initialized successfully")
    print(f"📁 Project root: {settings.project_root_path}")
    
    available_optional = [var for var, available in optional.items() if available]
    if available_optional:
        print(f"🔧 Optional services available: {', '.join(available_optional)}")

# Initialize on import (can be disabled for testing)
if os.getenv("SKIP_ENV_INIT") != "true":
    try:
        initialize_environment()
    except EnvironmentError as e:
        print(f"❌ Environment initialization failed: {e}")
        print("💡 Tip: Copy .env.template to .env and fill in your values")