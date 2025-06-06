"""
GitHub Integration for DigiNativa AI Team
=========================================

PURPOSE:
Enables the Projektledare to automatically monitor GitHub Issues,
process feature requests, create story breakdowns, and communicate
progress back to the human project owner.

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update REPO_OWNER and REPO_NAME in settings
2. Modify issue templates for your domain
3. Adjust status reporting for your workflow
4. Customize feature approval process for your stakeholders
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from github import Github, GithubException, Auth
    from github.Issue import Issue
    from github.PullRequest import PullRequest
except ImportError:
    print("⚠️  PyGithub not installed. Run: pip install PyGithub")
    Github = None
    GithubException = Exception
    Issue = None
    PullRequest = None
    Auth = None

from config.settings import SECRETS, GITHUB_CONFIG, PROJECT_ROOT
from workflows.status_handler import StatusHandler, report_success, report_error

class GitHubIntegration:
    """
    GitHub API integration for AI team coordination.
    
    RESPONSIBILITIES:
    - Monitor for new feature requests
    - Create story breakdown issues  
    - Update issue status based on agent progress
    - Handle human feedback and approvals
    - Manage sprint lifecycle communication
    """
    
    def __init__(self):
        """Initialize GitHub integration with authentication."""
        if Github is None:
            raise ImportError("PyGithub not installed. Run: pip install PyGithub")
            
        self.github_token = SECRETS.get("github_token")
        if not self.github_token or self.github_token.startswith("[YOUR_"):
            raise ValueError("GitHub token not configured. Set GITHUB_TOKEN in .env file")
        
        if Auth is not None:
            auth = Auth.Token(self.github_token)
            self.github = Github(auth=auth)
        else:
            # Fallback for older PyGithub versions
            self.github = Github(self.github_token)
        self.status_handler = StatusHandler()
        
        # Repository configuration
        self.repo_owner = GITHUB_CONFIG["ai_team_repo"]["owner"]
        self.repo_name = GITHUB_CONFIG["ai_team_repo"]["name"]
        self.repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        
        print(f"✅ GitHub integration initialized for {self.repo_owner}/{self.repo_name}")
    
    async def monitor_new_feature_requests(self) -> List[Dict[str, Any]]:
        """
        Monitor GitHub Issues for new feature requests.
        
        WORKFLOW:
        1. Scan for issues with 'feature' label that are 'open'
        2. Filter for issues not yet processed by AI team
        3. Return list of new feature requests for processing
        
        Returns:
            List of GitHub issue data ready for Projektledare analysis
        """
        try:
            # Get all open issues with 'feature' label
            issues = self.repo.get_issues(
                state='open',
                labels=['enhancement', 'ai-team']  # Updated to match your templates
            )
            
            new_feature_requests = []
            
            for issue in issues:
                # Check if issue has been processed by checking for AI team comments
                has_ai_response = False
                try:
                    comments = list(issue.get_comments())
                    has_ai_response = any(
                        comment.user.login == "github-actions[bot]" or 
                        "🤖 AI-Team Analysis" in comment.body
                        for comment in comments
                    )
                except Exception as e:
                    print(f"⚠️  Could not check comments for issue #{issue.number}: {e}")
                
                if not has_ai_response:
                    # Convert GitHub Issue to our format
                    issue_data = {
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body or "",
                        "labels": [{"name": label.name} for label in issue.labels],
                        "user": {"login": issue.user.login},
                        "state": issue.state,
                        "created_at": issue.created_at.isoformat(),
                        "url": issue.html_url,
                        "github_issue": issue  # Keep reference for updates
                    }
                    new_feature_requests.append(issue_data)
            
            print(f"📥 Found {len(new_feature_requests)} new feature requests to process")
            return new_feature_requests
            
        except GithubException as e:
            print(f"❌ GitHub API error: {e}")
            report_error("github_integration", "GITHUB_API_ERROR", str(e))
            return []
        except Exception as e:
            print(f"❌ Unexpected error monitoring issues: {e}")
            return []

    # Resten av metoderna från din ursprungliga kod...
    async def create_analysis_comment(self, issue_data: Dict[str, Any], 
                                    analysis_result: Dict[str, Any]) -> bool:
        """Post Projektledare's analysis results as a comment on the GitHub issue."""
        try:
            issue = issue_data["github_issue"]
            
            # Create formatted analysis comment
            comment_body = self._format_analysis_comment(analysis_result)
            
            # Post comment
            comment = issue.create_comment(comment_body)
            
            # Add labels based on analysis
            recommendation = analysis_result.get("recommendation", {})
            if recommendation.get("action") == "approve":
                issue.add_to_labels("ai-approved", "in-development")
            elif recommendation.get("action") == "clarify":
                issue.add_to_labels("needs-clarification")
            else:
                issue.add_to_labels("ai-review-needed")
            
            print(f"✅ Posted analysis comment on issue #{issue.number}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to post analysis comment: {e}")
            return False

    def _format_analysis_comment(self, analysis_result: Dict[str, Any]) -> str:
        """Format Projektledare analysis as GitHub comment."""
        recommendation = analysis_result.get("recommendation", {})
        dna_alignment = analysis_result.get("dna_alignment", {})
        complexity = analysis_result.get("complexity", {})
        
        return f"""## 🤖 AI-Team Analysis Results

### 📋 Analysis Summary
- **Recommendation**: {recommendation.get('action', 'unknown').upper()}
- **Priority**: {recommendation.get('priority', 'medium')}
- **Estimated Stories**: {complexity.get('estimated_stories', 'unknown')}
- **Estimated Duration**: {complexity.get('estimated_days', 'unknown')} days

### 🎯 DNA Alignment Check
- **Vision/Mission Aligned**: {'✅' if dna_alignment.get('vision_mission_aligned') else '❌'}
- **Target Audience Served**: {'✅' if dna_alignment.get('target_audience_served') else '❌'}
- **Design Principles Compatible**: {'✅' if dna_alignment.get('design_principles_compatible') else '❌'}

### 👥 Required Agents
{', '.join(complexity.get('required_agents', []))}

### 🔄 Next Steps
{recommendation.get('reasoning', 'Analysis complete - awaiting next steps')}

---
*Analysis completed by AI Projektledare using Claude-3.5-Sonnet*
"""


# Integration with Projektledare Agent
class ProjectOwnerCommunication:
    """
    High-level interface for Projektledare to communicate with project owner.
    """
    
    def __init__(self):
        self.github = GitHubIntegration()
        self.status_handler = StatusHandler()
    
    async def process_new_features(self) -> List[Dict[str, Any]]:
        """Main entry point for processing new feature requests."""
        # Get new feature requests
        new_requests = await self.github.monitor_new_feature_requests()
        
        processed_features = []
        
        for request in new_requests:
            try:
                print(f"🔍 Processing feature request #{request['number']}: {request['title']}")
                
                # We'll implement the actual processing later
                # For now, just create a mock analysis
                analysis = {
                    "recommendation": {"action": "approve", "priority": "medium"},
                    "dna_alignment": {"vision_mission_aligned": True},
                    "complexity": {"estimated_stories": 3, "required_agents": ["speldesigner", "utvecklare"]}
                }
                
                # Post analysis to GitHub
                await self.github.create_analysis_comment(request, analysis)
                
                processed_features.append({
                    "request": request,
                    "analysis": analysis,
                    "processed_at": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ Failed to process feature request #{request['number']}: {e}")
                report_error("project_owner_communication", "FEATURE_PROCESSING_ERROR", str(e))
        
        return processed_features
    
    async def check_for_approvals(self) -> List[Dict[str, Any]]:
        """Check for human approvals/rejections of completed features."""
        # Placeholder for now
        return []


# Factory function for easy integration
def create_project_owner_communication() -> ProjectOwnerCommunication:
    """Create and configure project owner communication system."""
    return ProjectOwnerCommunication()