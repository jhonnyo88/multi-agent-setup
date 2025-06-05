"""
DigiNativa Configuration Settings (Anthropic/Claude Version)
==========================================================

PURPOSE: 
Central configuration for all DigiNativa AI agents and tools, configured for Anthropic Claude.

ADAPTATION GUIDE:
🔧 Key settings to change for your project:
1. PROJECT_* variables: Update with your project details
2. GITHUB_* variables: Point to your repositories  
3. DOMAIN_* variables: Change from 'game_design' to your domain
4. TECH_STACK_* variables: Update to match your technology choices

ANTHROPIC INTEGRATION:
- Uses Claude-3-Sonnet for AI agent capabilities
- Configured for consistent, professional AI responses
- Optimized for complex reasoning and project management tasks

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
# AI AGENT CONFIGURATION (ANTHROPIC/CLAUDE)
# 🔧 ADAPT: Modify agent behavior for your domain
# ============================================================================

AGENT_CONFIG = {
    # Claude model configuration
    "llm_model": "claude-3-5-sonnet-20241022",  # Claude-3-Sonnet for balanced performance
    "max_iterations": 5,
    "temperature": 0.1,  # Low temperature for consistent, professional behavior
    
    # Claude-specific settings
    "max_tokens": 4000,  # Sufficient for complex analysis and reasoning
    "provider": "anthropic",
    "api_version": "2023-06-01",
    
    "domain_expertise": {
        "primary_domain": "pedagogical_game_design",  # 🔧 CHANGE: Your domain
        "secondary_domains": ["public_sector", "digitalization"],  # 🔧 CHANGE: Related domains
        "technical_focus": ["react", "fastapi", "game_mechanics"],  # 🔧 CHANGE: Your tech focus
        "ai_capabilities": [
            "complex_reasoning", 
            "strategic_planning", 
            "requirement_analysis",
            "problem_decomposition"
        ]
    },
    
    # Communication style for Claude
    "communication_style": {
        "tone": "professional",
        "format": "structured_json",
        "detail_level": "comprehensive",
        "reasoning_transparency": "high"
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
    },
    "ai_quality": {
        "response_consistency": 0.9,  # Claude responses should be highly consistent
        "reasoning_clarity": "high",   # Claude should explain its reasoning
        "decision_accuracy": 0.85      # Target accuracy for AI decisions
    }
}

# ============================================================================
# SENSITIVE CONFIGURATION (from environment variables)
# 🔒 NEVER commit actual values - use .env file
# ============================================================================

SECRETS = {
    # Anthropic Claude API configuration
    "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", "[YOUR_ANTHROPIC_API_KEY]"),
    
    # GitHub integration
    "github_token": os.getenv("GITHUB_TOKEN", "[YOUR_GITHUB_TOKEN]"),
    
    # Optional integrations
    "netlify_token": os.getenv("NETLIFY_TOKEN", "[YOUR_NETLIFY_TOKEN]"),
    "webhook_secret": os.getenv("WEBHOOK_SECRET", "[YOUR_WEBHOOK_SECRET]"),
    
    # Alternative AI providers (optional)
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),  # For fallback if needed
}

# Validate that required secrets are present
REQUIRED_SECRETS = ["anthropic_api_key", "github_token"]
for secret in REQUIRED_SECRETS:
    if SECRETS[secret].startswith("[YOUR_"):
        print(f"⚠️  WARNING: {secret} not configured. Check your .env file.")
        print(f"   Required for: {'Claude AI agents' if secret == 'anthropic_api_key' else 'GitHub integration'}")

# Validate Claude API key format
if SECRETS["anthropic_api_key"] and not SECRETS["anthropic_api_key"].startswith("sk-ant-"):
    print(f"⚠️  WARNING: anthropic_api_key may be invalid. Should start with 'sk-ant-'")

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

# ============================================================================
# ANTHROPIC-SPECIFIC CONFIGURATION
# 🔧 ADAPT: Adjust Claude behavior for your domain
# ============================================================================

CLAUDE_CONFIG = {
    "system_prompts": {
        "projektledare": (
            "You are an expert AI project manager specializing in software development coordination. "
            "You excel at breaking down complex requirements, coordinating teams, and ensuring quality delivery. "
            "Always provide structured, reasoned responses with clear next steps."
        ),
        "speldesigner": (
            "You are an expert in game design and user experience, specializing in educational games. "
            "You create engaging, pedagogical experiences that serve professional learners effectively."
        ),
        "utvecklare": (
            "You are an expert full-stack developer specializing in React and FastAPI. "
            "You write clean, efficient, well-tested code following best practices."
        ),
        # 🔧 ADAPT: Add system prompts for your domain-specific agents
    },
    
    "reasoning_requirements": {
        "always_explain_decisions": True,
        "show_consideration_of_alternatives": True,
        "reference_project_dna": True,
        "structured_output_format": "json"
    },
    
    "quality_controls": {
        "consistency_checking": True,
        "fact_verification": True,
        "reasoning_validation": True
    }
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "claude_interactions": True,  # Log Claude API interactions for debugging
    "agent_decisions": True,      # Log agent decision reasoning
    "workflow_steps": True        # Log workflow progression
}

# ============================================================================
# DEVELOPMENT vs PRODUCTION SETTINGS
# ============================================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    AGENT_CONFIG["temperature"] = 0.05  # Even more consistent in production
    LOGGING_CONFIG["level"] = "WARNING"
    CLAUDE_CONFIG["quality_controls"]["fact_verification"] = True
elif ENVIRONMENT == "development":
    AGENT_CONFIG["temperature"] = 0.1   # Slightly more creative in dev
    LOGGING_CONFIG["level"] = "DEBUG"
    CLAUDE_CONFIG["quality_controls"]["fact_verification"] = False

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_configuration():
    """
    Validate that all required configuration is present and valid.
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # Check required environment variables
    for secret in REQUIRED_SECRETS:
        if not SECRETS[secret] or SECRETS[secret].startswith("[YOUR_"):
            errors.append(f"Missing required secret: {secret}")
    
    # Validate Claude API key format
    if SECRETS["anthropic_api_key"] and not SECRETS["anthropic_api_key"].startswith("sk-ant-"):
        errors.append("Anthropic API key format invalid (should start with 'sk-ant-')")
    
    # Check directory structure
    required_dirs = [DNA_DIR, STATE_DIR]
    for dir_path in required_dirs:
        if not dir_path.exists():
            errors.append(f"Required directory missing: {dir_path}")
    
    return len(errors) == 0, errors

def get_claude_model_info():
    """Get information about the configured Claude model."""
    return {
        "model": AGENT_CONFIG["llm_model"],
        "provider": "Anthropic",
        "max_tokens": AGENT_CONFIG["max_tokens"],
        "temperature": AGENT_CONFIG["temperature"],
        "capabilities": AGENT_CONFIG["domain_expertise"]["ai_capabilities"]
    }

# Initialize configuration validation
if __name__ == "__main__":
    is_valid, errors = validate_configuration()
    if is_valid:
        print("✅ Configuration validation passed")
        print(f"🤖 Claude model: {get_claude_model_info()['model']}")
    else:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"   - {error}")