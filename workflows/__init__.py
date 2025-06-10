"""
Simplified Workflows Package for DigiNativa AI Team
==================================================

PURPOSE:
Contains essential workflow management with simplified architecture.
No complex coordination or exception handling - just core functionality.

SIMPLIFIED MODULES:
- status_handler: Basic status communication between agents
- github_integration: GitHub API integration for project owner communication

REMOVED COMPLEXITY:
- Agent coordinator (caused circular imports)
- Auto implementation (over-engineered)
- Exception handler (too complex for current needs)
- Cross-repo sync (not needed)

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update status codes in status_handler.py for your workflow
2. Modify GitHub integration for your repository structure
3. Add workflow modules only when actually needed
"""

from .status_handler import StatusHandler, report_success, report_error, get_agent_status

# Import GitHub integration with error handling
try:
    from .github_integration.project_owner_communication import (
        ProjectOwnerCommunication, 
        GitHubIntegration
    )
    GITHUB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  GitHub integration not available: {e}")
    GITHUB_AVAILABLE = False
    ProjectOwnerCommunication = None
    GitHubIntegration = None

__all__ = [
    "StatusHandler",
    "report_success", 
    "report_error",
    "get_agent_status"
]

# Add GitHub exports if available
if GITHUB_AVAILABLE:
    __all__.extend([
        "ProjectOwnerCommunication",
        "GitHubIntegration"
    ])

def get_workflow_status():
    """Get status of available workflow components."""
    return {
        "status_handler": True,  # Always available
        "github_integration": GITHUB_AVAILABLE,
        "simplified_architecture": True,
        "removed_components": [
            "agent_coordinator", 
            "auto_implementation",
            "exception_handler", 
            "cross_repo_sync"
        ]
    }

# Export get_workflow_status function for tests
__all__.append("get_workflow_status")

def test_workflows():
    """Test that workflow components work."""
    print("🧪 Testing Simplified Workflows...")
    
    # Test status handler
    try:
        status_handler = StatusHandler()
        print("✅ StatusHandler: Working")
    except Exception as e:
        print(f"❌ StatusHandler: Failed - {e}")
    
    # Test GitHub integration
    if GITHUB_AVAILABLE:
        try:
            # Don't actually create (requires credentials)
            print("✅ GitHub Integration: Available") 
        except Exception as e:
            print(f"❌ GitHub Integration: Failed - {e}")
    else:
        print("⚠️  GitHub Integration: Not available")
    
    print("🎉 Workflow test complete!")

if __name__ == "__main__":
    test_workflows()