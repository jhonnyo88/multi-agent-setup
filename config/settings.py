"""
DigiNativa Configuration Settings
================================

PURPOSE: 
Central configuration for all DigiNativa AI agents and tools.

ADAPTATION GUIDE:
🔧 Key settings to change for your project:
1. PROJECT_* variables: Update with your project details
2. GITHUB_* variables: Point to your repositories  
3. DOMAIN_* variables: Change from 'game_design' to your domain
4. TECH_STACK_* variables: Update to match your technology choices

SECURITY NOTE:
🔒 Never commit real API keys! Use .env file for secrets.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# PROJECT CONFIGURATION
# 🔧 ADAPT: Change these for your project
# ============================================================================

PROJECT_NAME = "DigiNativa"
PROJECT_DOMAIN = "game_development"  # 🔧 CHANGE: 'e_commerce', 'mobile_app', 'saas', etc.
PROJECT_DESCRIPTION = "Interactive learning game for digitalization strategy"

# Target audience configuration
TARGET_AUDIENCE = {
    "primary_persona": "Anna",  # 🔧 CHANGE: Your user persona name
    "description": "Offentlig förvaltare, upptagen professionell",  # 🔧 CHANGE: Your persona description
    "technical_level": "intermediate",  # 🔧 CHANGE: 'beginner', 'intermediate', 'expert'
    "time_constraints": "< 10 minutes per session"  # 🔧 CHANGE: Your time constraints
}

# ============================================================================
# REPOSITORY CONFIGURATION  
# 🔧 ADAPT: Point to your GitHub repositories
# ============================================================================

GITHUB_CONFIG = {
    "ai_team_repo": {
        "owner": os.getenv("AI_TEAM_REPO_OWNER", "jhonnyo88"),
        "name": os.getenv("AI_TEAM_REPO_NAME", "multi-agent-setup"),
        "branch": "main"
    },
    "project_repo": {
        "owner": os.getenv("PROJECT_REPO_OWNER", "jhonnyo88"),
        "name": os.getenv("PROJECT_REPO_NAME", "diginativa-game"),
        "branch": "main"
    }
}

# ============================================================================
# TECHNOLOGY STACK
# 🔧 ADAPT: Update to match your tech choices
# ============================================================================

TECH_STACK = {
    "frontend": {
        "framework": "React",  # 🔧 CHANGE: 'Vue', 'Angular', 'Svelte', etc.
        "language": "JavaScript",  # 🔧 CHANGE: 'TypeScript', etc.
        "styling": "Tailwind CSS"  # 🔧 CHANGE: 'Bootstrap', 'Material-UI', etc.
    },
    "backend": {
        "framework": "FastAPI",  # 🔧 CHANGE: 'Django', 'Flask', 'Node.js', etc.
        "language": "Python",  # 🔧 CHANGE: 'JavaScript', 'Go', 'Java', etc.
        "database": "SQLite"  # 🔧 CHANGE: 'PostgreSQL', 'MongoDB', etc.
    },
    "deployment": {
        "platform": "Netlify",  # 🔧 CHANGE: 'Vercel', 'AWS', 'Heroku', etc.
        "type": "serverless"  # 🔧 CHANGE: 'container', 'vm', etc.
    }
}

# ============================================================================
# AI AGENT CONFIGURATION
# 🔧 ADAPT: Modify agent behavior for your domain
# ============================================================================

AGENT_CONFIG = {
    "llm_model": "gpt-4",  # 🔧 CHANGE: 'claude-3-sonnet', 'gpt-3.5-turbo', etc.
    "max_iterations": 5,
    "temperature": 0.1,  # Low temperature for consistent behavior
    
    "domain_expertise": {
        "primary_domain": "pedagogical_game_design",  # 🔧 CHANGE: Your domain
        "secondary_domains": ["public_sector", "digitalization"],  # 🔧 CHANGE: Related domains
        "technical_focus": ["react", "fastapi", "game_mechanics"]  # 🔧 CHANGE: Your tech focus
    }
}

# ============================================================================
# QUALITY GATES & STANDARDS
# 🔧 ADAPT: Set quality thresholds for your project type
# ============================================================================

QUALITY_STANDARDS = {
    "code_quality": {
        "eslint_max_warnings": 0,
        "test_coverage_minimum": 80,  # 🔧 CHANGE: Based on your requirements
        "complexity_threshold": 10
    },
    "performance": {
        "lighthouse_performance": 90,  # 🔧 CHANGE: Based on your performance needs
        "lighthouse_accessibility": 95,
        "bundle_size_limit_mb": 2  # 🔧 CHANGE: Based on your app type
    },
    "user_experience": {
        "max_session_duration": 600,  # 10 minutes for games, 🔧 CHANGE for other domains
        "max_clicks_to_complete": 20,  # 🔧 CHANGE: Based on your UX requirements
        "mobile_responsive": True
    }
}

# ============================================================================
# SENSITIVE CONFIGURATION (from environment variables)
# 🔒 NEVER commit actual values - use .env file
# ============================================================================

SECRETS = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", "[YOUR_OPENAI_API_KEY]"),
    "github_token": os.getenv("GITHUB_TOKEN", "[YOUR_GITHUB_TOKEN]"),
    "netlify_token": os.getenv("NETLIFY_TOKEN", "[YOUR_NETLIFY_TOKEN]"),
    "webhook_secret": os.getenv("WEBHOOK_SECRET", "[YOUR_WEBHOOK_SECRET]")
}

# Validate that required secrets are present
REQUIRED_SECRETS = ["openai_api_key", "github_token"]
for secret in REQUIRED_SECRETS:
    if SECRETS[secret].startswith("[YOUR_"):
        print(f"⚠️  WARNING: {secret} not configured. Check your .env file.")

# ============================================================================
# PATHS & DIRECTORIES
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
DNA_DIR = DOCS_DIR / "dna"
STATE_DIR = PROJECT_ROOT / "state"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Ensure critical directories exist
STATE_DIR.mkdir(exist_ok=True)
(STATE_DIR / "logs").mkdir(exist_ok=True)