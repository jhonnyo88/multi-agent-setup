"""
GitHub Integration Package for DigiNativa AI Team
================================================

This package handles all GitHub API integration for the AI team,
including issue monitoring, progress reporting, and project owner communication.
"""

from .project_owner_communication import GitHubIntegration, ProjectOwnerCommunication

__all__ = [
    "GitHubIntegration",
    "ProjectOwnerCommunication"
]