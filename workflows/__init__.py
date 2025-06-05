"""
Workflows package for DigiNativa AI-Team
=======================================

PURPOSE:
Contains workflow management, status handling, and exception handling
for coordinating the AI team's work.

MODULES:
- status_handler: Centralized status management for agent communication
- exception_handler: Automated exception resolution and escalation
- story_lifecycle: Story progression management
- github_integration: GitHub API integration for issue management
- cross_repo_sync: Synchronization between AI-team and project repos

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update status codes in status_handler.py for your domain
2. Modify exception patterns in exception_handler.py for your workflow
3. Customize GitHub integration for your repository structure
"""

from .status_handler import StatusHandler, report_success, report_error, get_agent_status
from .exception_handler import ExceptionHandler, handle_agent_exception

__all__ = [
    "StatusHandler",
    "ExceptionHandler", 
    "report_success",
    "report_error",
    "get_agent_status",
    "handle_agent_exception"
]