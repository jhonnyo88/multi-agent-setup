"""
DigiNativa AI-Team: Base Configuration
=====================================

PURPOSE: Global system configuration and settings management

MODULAR DESIGN:
- Centralized configuration for all modules
- Environment-specific settings
- Secure secrets management
- Adaptation points clearly marked

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update PROJECT_DOMAIN and PROJECT_NAME
2. Modify AGENT_ROLES for your domain specialists  
3. Adjust QUALITY_GATES for your quality requirements
4. Update GITHUB_SETTINGS for your repositories

VERSION: 1.0.0
CREATED: 2025-06-10
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseSettings, Field

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

class DigiNativaSettings(BaseSettings):
    """
    Core configuration for DigiNativa AI-Team
    
    🔧 ADAPTATION POINTS:
    - Change project_domain for your domain (e.g., "e_commerce", "mobile_app")
    - Update agent_roles for your specialist types
    - Modify quality_gates for your quality requirements
    """
    
    # 🔧 ADAPT: Core project identity
    project_name: str = "DigiNativa AI-Team"
    project_domain: str = "educational_game"  # 🔧 CHANGE: Your domain
    version: str = "1.0.0"
    
    # 🔧 ADAPT: Environment configuration  
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=True, env="DEBUG")
    
    # 🔧 ADAPT: AI Service Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_ai_model: str = "claude-3-5-sonnet-20241022"  # 🔧 CHANGE: Your preferred model
    
    # 🔧 ADAPT: GitHub Configuration  
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    github_repo_owner: str = Field(default="jhonnyo88", env="GITHUB_REPO_OWNER")  # 🔧 CHANGE
    github_repo_name: str = Field(default="multi-agent-setup", env="GITHUB_REPO_NAME")  # 🔧 CHANGE
    
    # 🔧 ADAPT: Database Configuration
    database_url: str = Field(default="sqlite:///ai_team.db", env="DATABASE_URL")
    
    # 🔧 ADAPT: Agent Configuration
    agent_roles: Dict[str, str] = {
        "projektledare": "Team Orchestrator and Project Manager",
        "speldesigner": "Educational Game Designer",  # 🔧 CHANGE: Your domain designer
        "utvecklare": "Full-Stack Developer (React + FastAPI)",  # 🔧 CHANGE: Your tech stack
        "testutvecklare": "Test Automation Engineer", 
        "qa_testare": "Manual QA and User Perspective Tester",
        "kvalitetsgranskare": "Code Quality and Performance Reviewer"
    }
    
    # 🔧 ADAPT: Quality Requirements
    quality_gates: Dict[str, Any] = {
        "code_coverage_minimum": 0.90,  # 90% coverage required
        "lighthouse_score_minimum": 90,   # Lighthouse performance score
        "accessibility_level": "WCAG_2_1_AA",
        "performance_budget": {
            "bundle_size_kb": 500,
            "load_time_seconds": 3.0,
            "api_response_ms": 500
        }
    }
    
    # 🔧 ADAPT: Workflow Configuration
    workflow_settings: Dict[str, Any] = {
        "github_polling_interval_minutes": 5,
        "max_qa_iterations": 3,  # Deadlock prevention
        "story_timeout_hours": 48,
        "auto_deploy_on_approval": True
    }
    
    # Computed properties
    @property
    def github_repo_url(self) -> str:
        return f"https://github.com/{self.github_repo_owner}/{self.github_repo_name}"
    
    @property
    def project_root_path(self) -> Path:
        return PROJECT_ROOT
    
    @property
    def logs_directory(self) -> Path:
        logs_dir = PROJECT_ROOT / "reports" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir
    
    @property
    def specs_directory(self) -> Path:
        specs_dir = PROJECT_ROOT / "reports" / "specs"
        specs_dir.mkdir(parents=True, exist_ok=True)
        return specs_dir

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = DigiNativaSettings()

# Export commonly used values
PROJECT_NAME = settings.project_name
PROJECT_DOMAIN = settings.project_domain
PROJECT_ROOT = settings.project_root_path
AGENT_ROLES = settings.agent_roles
QUALITY_GATES = settings.quality_gates