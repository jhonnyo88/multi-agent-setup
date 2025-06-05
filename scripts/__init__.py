"""
Setup and utility scripts for DigiNativa AI-Team
===============================================

PURPOSE:
This package contains command-line scripts for setting up, deploying,
and managing the DigiNativa AI-Team system.

SCRIPTS INCLUDED:
- setup.py: Interactive setup wizard for initial configuration
- deploy_agents.py: Start and manage the AI agent team
- health_check.py: Monitor system health and agent status
- sync_repos.py: Manual synchronization between AI-team and game repos
- backup_state.py: Backup and restore agent state and memory

ADAPTATION GUIDE:
🔧 To adapt these scripts for your project:
1. Update repository URLs in sync_repos.py
2. Modify health checks for your specific integrations
3. Add deployment scripts for your target platform
4. Customize backup procedures for your data requirements

USAGE:
Run scripts from project root directory:
    python scripts/setup.py        # First-time setup
    python scripts/deploy_agents.py # Start AI team
    python scripts/health_check.py  # Check system status
"""

__version__ = "1.0.0"
__author__ = "DigiNativa Team"