"""
Enhanced GitHub Integration for DigiNativa AI Team
================================================

PURPOSE:
Complete GitHub API integration that actually posts AI analysis results
to GitHub Issues and manages the full workflow.

WHAT'S NEW:
- Real GitHub API posting (not just mock)
- Better error handling and validation
- Structured comment formatting for humans
- Issue labeling based on AI analysis
- Story breakdown issue creation
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from .enhanced_workflow import EnhancedGitHubWorkflow

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
    Complete GitHub API integration for AI team coordination.
    
    RESPONSIBILITIES:
    - Monitor for new feature requests
    - Post AI analysis results as comments
    - Create story breakdown issues
    - Update issue labels based on analysis
    - Handle human feedback and approvals
    """
    
    def __init__(self):
        """Initialize GitHub integration with proper authentication."""
        if Github is None:
            raise ImportError("PyGithub not installed. Run: pip install PyGithub")
            
        # Get and validate GitHub token
        self.github_token = SECRETS.get("github_token")
        if not self.github_token or self.github_token.startswith("[YOUR_"):
            raise ValueError(
                "GitHub token not configured. Set GITHUB_TOKEN in .env file.\n"
                "See docs/setup/github_token_setup.md for instructions."
            )
        
        try:
            # Use modern PyGithub authentication
            auth = Auth.Token(self.github_token)
            self.github = Github(
                auth=auth,
                user_agent="DigiNativa-AI-Team/1.0"
            )
            
            # Test authentication
            authenticated_user = self.github.get_user()
            print(f"✅ GitHub authenticated as: {authenticated_user.login}")
            
            # Set up repository references
            self.ai_repo_config = GITHUB_CONFIG["ai_team_repo"]
            self.project_repo_config = GITHUB_CONFIG["project_repo"]
            
            # Get AI team repository (where we post analysis)
            self.ai_repo = self.github.get_repo(
                f"{self.ai_repo_config['owner']}/{self.ai_repo_config['name']}"
            )
            
            # Get project repository (where stories are created)  
            self.project_repo = self.github.get_repo(
                f"{self.project_repo_config['owner']}/{self.project_repo_config['name']}"
            )
            
            print(f"✅ GitHub repos connected:")
            print(f"   AI Team: {self.ai_repo.full_name}")
            print(f"   Project: {self.project_repo.full_name}")
            
        except GithubException as e:
            if e.status == 401:
                print("❌ GitHub API Error: 401 Unauthorized")
                print("   Your GitHub token may be invalid or expired")
                print("   Make sure the token has 'repo' permissions")
                print("   Generate a new token at: https://github.com/settings/tokens")
            else:
                print(f"❌ GitHub API Error: {e.status} - {e.data.get('message', 'Unknown error')}")
            raise
        except Exception as e:
            print(f"❌ Unexpected GitHub error: {e}")
            raise
    
    async def monitor_new_feature_requests(self) -> List[Dict[str, Any]]:
        """
        Scan GitHub Issues for new feature requests that need AI analysis.
        
        DETECTION LOGIC:
        1. Look for issues with 'enhancement' or 'ai-team' labels
        2. Check if issue already has AI analysis comment
        3. Return unprocessed issues for Projektledare analysis
        
        Returns:
            List of GitHub issues ready for AI processing
        """
        try:
            print("🔍 Scanning for new feature requests...")
            
            # Get open issues with relevant labels
            issues = self.project_repo.get_issues(
                state='open',
                labels=['enhancement', 'ai-team']
            )
            
            new_feature_requests = []
            
            for issue in issues:
                print(f"   Checking issue #{issue.number}: {issue.title}")
                
                # Check if AI has already analyzed this issue
                has_ai_analysis = await self._check_for_ai_analysis(issue)
                
                if not has_ai_analysis:
                    print(f"   ✅ Found new feature request: #{issue.number}")
                    
                    # Convert to our standard format
                    issue_data = {
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body or "",
                        "labels": [{"name": label.name} for label in issue.labels],
                        "user": {"login": issue.user.login},
                        "state": issue.state,
                        "created_at": issue.created_at.isoformat(),
                        "updated_at": issue.updated_at.isoformat(),
                        "url": issue.html_url,
                        "github_issue": issue  # Keep reference for updates
                    }
                    new_feature_requests.append(issue_data)
                else:
                    print(f"   ⏭️  Already processed: #{issue.number}")
            
            print(f"📥 Found {len(new_feature_requests)} new requests to process")
            return new_feature_requests
            
        except GithubException as e:
            print(f"❌ GitHub API error while monitoring: {e}")
            report_error("github_integration", "MONITOR_ERROR", str(e))
            return []
        except Exception as e:
            print(f"❌ Unexpected error monitoring issues: {e}")
            return []
    
    async def _check_for_ai_analysis(self, issue: Issue) -> bool:
        """Check if an issue already has AI analysis comments."""
        try:
            comments = list(issue.get_comments())
            
            for comment in comments:
                # Look for AI analysis markers in comment body
                if ("🤖 AI-Team Analysis" in comment.body or 
                    "AI Projektledare" in comment.body or
                    comment.user.login == "github-actions[bot]"):
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Could not check comments for issue #{issue.number}: {e}")
            return False  # Assume not processed to be safe
    
    async def post_analysis_results(self, issue_data: Dict[str, Any], 
                                  analysis_result: Dict[str, Any]) -> bool:
        """
        Post Projektledare's analysis results as a comment on the GitHub issue.
        
        This is the key function that makes AI analysis visible to humans.
        
        Args:
            issue_data: The GitHub issue data
            analysis_result: The Projektledare's analysis
            
        Returns:
            True if comment was posted successfully
        """
        try:
            issue = issue_data["github_issue"]
            
            print(f"📝 Posting AI analysis to issue #{issue.number}...")
            
            # Create formatted comment
            comment_body = self._format_analysis_comment(analysis_result, issue_data)
            
            # Post the comment
            comment = issue.create_comment(comment_body)
            
            # Update issue labels based on analysis
            await self._update_issue_labels(issue, analysis_result)
            
            print(f"✅ Posted analysis comment: {comment.html_url}")
            
            # Log success
            report_success(
                "github_integration", 
                "ANALYSIS_POSTED",
                issue_number=issue.number,
                comment_id=comment.id,
                recommendation=analysis_result.get("recommendation", {}).get("action")
            )
            
            return True
            
        except GithubException as e:
            print(f"❌ GitHub API error posting comment: {e}")
            report_error("github_integration", "COMMENT_POST_ERROR", str(e))
            return False
        except Exception as e:
            print(f"❌ Error posting analysis comment: {e}")
            return False
    
    def _format_analysis_comment(self, analysis: Dict[str, Any], 
                                issue_data: Dict[str, Any]) -> str:
        """
        Format AI analysis as a human-readable GitHub comment.
        
        DESIGN GOALS:
        - Clear, professional presentation
        - Actionable information for project owner
        - Links to next steps in workflow
        - Swedish language for project communication
        """
        recommendation = analysis.get("recommendation", {})
        dna_alignment = analysis.get("dna_alignment", {})
        complexity = analysis.get("complexity", {})
        risk_assessment = analysis.get("risk_assessment", {})
        
        # Main recommendation
        action = recommendation.get("action", "unknown").upper()
        reasoning = recommendation.get("reasoning", "Ingen motivering angiven")
        
        # Status emoji based on recommendation
        status_emoji = {
            "APPROVE": "✅",
            "REJECT": "❌", 
            "CLARIFY": "❓",
            "DEFER": "⏸️"
        }.get(action, "🤖")
        
        comment = f"""## {status_emoji} AI-Team Analys Slutförd

### 📋 Analysresultat
- **Rekommendation**: {action}
- **Prioritet**: {recommendation.get('priority', 'medium')}
- **Estimerade Stories**: {complexity.get('estimated_stories', 'okänt')}
- **Estimerad tid**: {complexity.get('estimated_days', 'okänt')} dagar

### 🎯 DNA-Kontroll (Projektmål)
"""
        
        # DNA Alignment details
        if dna_alignment:
            vision_ok = "✅" if dna_alignment.get('vision_mission_aligned') else "❌"
            audience_ok = "✅" if dna_alignment.get('target_audience_served') else "❌"
            principles_ok = "✅" if dna_alignment.get('design_principles_compatible') else "❌"
            
            comment += f"""- **Vision/Mission-anpassad**: {vision_ok}
- **Målgrupp (Anna) tjänas**: {audience_ok}
- **Designprinciper kompatibla**: {principles_ok}
"""
            
            if dna_alignment.get("concerns"):
                comment += f"\n**⚠️ Identifierade bekymmer:**\n"
                for concern in dna_alignment["concerns"]:
                    comment += f"- {concern}\n"
        
        # Required agents
        if complexity.get("required_agents"):
            comment += f"""
### 👥 Krävda AI-Agenter
{', '.join(complexity.get('required_agents', []))}
"""
        
        # Risk assessment
        if risk_assessment.get("technical_risks") or risk_assessment.get("ux_risks"):
            comment += f"\n### ⚠️ Riskbedömning\n"
            
            if risk_assessment.get("technical_risks"):
                comment += "**Tekniska risker:**\n"
                for risk in risk_assessment["technical_risks"]:
                    comment += f"- {risk}\n"
            
            if risk_assessment.get("ux_risks"):
                comment += "**UX-risker:**\n" 
                for risk in risk_assessment["ux_risks"]:
                    comment += f"- {risk}\n"
        
        # Next steps based on recommendation
        comment += f"\n### 🚀 Nästa Steg\n"
        
        if action == "APPROVE":
            comment += """AI-teamet kommer nu att:
1. 📋 Skapa detaljerade stories för implementation
2. 🎨 Speldesigner skapar UX-specifikation
3. 💻 Utvecklare implementerar funktion
4. 🧪 Testutvecklare skapar automatiska tester
5. 🔍 QA-testare validerar från Annas perspektiv

**Förväntad leveranstid**: {estimated_days} dagar""".format(
                estimated_days=complexity.get('estimated_days', '4-6')
            )
        elif action == "CLARIFY":
            comment += f"**Behöver förtydligande**: {reasoning}\n\n"
            comment += "Vänligen uppdatera issue-beskrivningen med mer detaljer och tagga @ai-team för omanalys."
        elif action == "REJECT":
            comment += f"**Ej godkänd**: {reasoning}\n\n"
            comment += "Överväg att revidera feature-förfrågan så den bättre matchar projektets mål och designprinciper."
        
        # Footer
        comment += f"""

---
*Analys genomförd av AI Projektledare (Claude-3.5-Sonnet) • {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Issue #{issue_data['number']} • DigiNativa AI-Team v1.0*"""
        
        return comment
    
    async def create_story_as_child_issue(self, parent_issue: Issue, story_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a story issue as child of parent feature issue.
        
        Uses GitHub's issue linking to establish parent-child relationship.
        """
        try:
            # Create story title with parent reference
            story_title = f"[STORY] {story_data['title']}"
            
            # Create story body with parent link
            story_body = f"""## 📋 Story from Feature #{parent_issue.number}

    **Parent Feature**: #{parent_issue.number} - {parent_issue.title}
    **Story ID**: {story_data['story_id']}
    **Assigned Agent**: {story_data['assigned_agent']}
    **Story Type**: {story_data['story_type']}
    **Estimated Effort**: {story_data['estimated_effort']}

    ### 📝 Description
    {story_data['description']}

    ### ✅ Acceptance Criteria
    """
            
            for criterion in story_data['acceptance_criteria']:
                story_body += f"- [ ] {criterion}\n"
            
            if story_data.get('dependencies'):
                story_body += f"\n### 🔗 Dependencies\n"
                for dep in story_data['dependencies']:
                    story_body += f"- {dep}\n"
            
            story_body += f"""
    ### 🎯 Design Principles Addressed
    {', '.join(story_data.get('design_principles_addressed', []))}

    ### 🤖 AI Team Information
    **Responsible Agent**: {story_data['assigned_agent']}
    **Created by**: AI Projektledare
    **Parent Feature**: #{parent_issue.number}

    ---
    *This story is part of automated workflow for Feature #{parent_issue.number}*
    *Development will be tracked through linked pull requests*
    """
            
            # Create the story issue
            story_issue = self.project_repo.create_issue(
                title=story_title,
                body=story_body,
                labels=[
                    'story', 
                    'ai-generated', 
                    f'agent-{story_data["assigned_agent"]}',
                    f'effort-{story_data["estimated_effort"].lower()}',
                    f'parent-{parent_issue.number}'  # NEW: Parent tracking label
                ]
            )
            
            # Link story to parent using GitHub's development field
            # This is done through issue comments with special keywords
            link_comment = f"""**🔗 Linked to Parent Feature**

    This story is part of #{parent_issue.number}

    Development progress will be tracked through pull requests that reference both this story and the parent feature.
    """
            story_issue.create_comment(link_comment)
            
            # Update parent issue with child reference
            parent_comment = f"""**📋 Story Created: #{story_issue.number}**

    - **Story**: {story_data['story_id']} - {story_data['title']}
    - **Agent**: {story_data['assigned_agent']}
    - **Type**: {story_data['story_type']}
    - **Link**: #{story_issue.number}
    """
            parent_issue.create_comment(parent_comment)
            
            print(f"✅ Created child story #{story_issue.number} linked to parent #{parent_issue.number}")
            
            return {
                "story_id": story_data['story_id'],
                "github_issue": story_issue,
                "number": story_issue.number,
                "url": story_issue.html_url,
                "parent_issue_number": parent_issue.number,
                "assigned_agent": story_data['assigned_agent']
            }
            
        except Exception as e:
            print(f"❌ Failed to create child story: {e}")
            return None

    async def monitor_project_repo_for_features(self) -> List[Dict[str, Any]]:
        """Monitor project repository for ALL types of issues that AI should handle."""
        try:
            # Get ALL open issues with AI-relevant labels from PROJECT repo
            ai_relevant_labels = [
                'ai-team',           # General AI team issues
                'feature',           # Feature requests
                'enhancement',       # Enhancement requests  
                'feature-approval',  # Approval requests
                'escalation',        # Escalation requests
                'bug'               # Bug reports that AI should handle
            ]
            
            # Check for any issue with AI-relevant labels
            issues = self.project_repo.get_issues(
                state='open',
                labels=ai_relevant_labels
            )
            
            ai_actionable_issues = []
            
            for issue in issues:
                # Determine issue type and if AI should act
                issue_type = self._determine_issue_type(issue)
                needs_ai_action = await self._check_if_ai_should_act(issue, issue_type)
                
                if needs_ai_action:
                    ai_actionable_issues.append({
                        "issue_type": issue_type,
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body or "",
                        "labels": [{"name": label.name} for label in issue.labels],
                        "user": {"login": issue.user.login},
                        "state": issue.state,
                        "created_at": issue.created_at.isoformat(),
                        "updated_at": issue.updated_at.isoformat(),
                        "url": issue.html_url,
                        "github_issue": issue,
                        "repository": "project_repo"
                    })
            
            return ai_actionable_issues
            
        except Exception as e:
            print(f"❌ Error monitoring project repo: {e}")
            return []

    def _determine_issue_type(self, issue) -> str:
        """Determine what type of issue this is."""
        title = issue.title.lower()
        labels = [label.name.lower() for label in issue.labels]
        
        if any(label in labels for label in ['feature', 'enhancement']):
            return "feature_request"
        elif 'feature-approval' in labels or '[approval]' in title:
            return "feature_approval"
        elif 'escalation' in labels or '[escalation]' in title:
            return "escalation_request"
        elif 'bug' in labels:
            return "bug_report"
        else:
            return "unknown"

    async def _check_if_ai_should_act(self, issue, issue_type: str) -> bool:
        """Check if AI team should take action on this issue."""
        
        # Always act on new feature requests
        if issue_type == "feature_request":
            return not await self._check_for_ai_analysis(issue)
        
        # Act on feature approvals that AI hasn't processed
        elif issue_type == "feature_approval":
            return not await self._check_for_ai_response(issue)
        
        # Act on escalations that need AI response
        elif issue_type == "escalation_request":
            return await self._check_if_escalation_needs_response(issue)
        
        # Act on bugs if configured to do so
        elif issue_type == "bug_report":
            return await self._check_if_bug_needs_ai_action(issue)
        
        return False

    async def _update_issue_labels(self, issue: Issue, analysis: Dict[str, Any]):
        """Update issue labels based on AI analysis results."""
        try:
            recommendation = analysis.get("recommendation", {})
            action = recommendation.get("action", "").lower()
            
            # Remove any existing AI labels
            existing_labels = [label.name for label in issue.labels]
            ai_labels_to_remove = [label for label in existing_labels 
                                 if label.startswith("ai-") and label != "ai-team"]
            
            for label in ai_labels_to_remove:
                try:
                    issue.remove_from_labels(label)
                except:
                    pass  # Label might not exist
            
            # Add new labels based on analysis
            if action == "approve":
                issue.add_to_labels("ai-approved", "in-development")
                
                # Add priority label
                priority = recommendation.get("priority", "medium")
                issue.add_to_labels(f"priority-{priority}")
                
            elif action == "clarify":
                issue.add_to_labels("ai-needs-clarification", "blocked")
                
            elif action == "reject":
                issue.add_to_labels("ai-rejected")
            
            # Add complexity label
            complexity = analysis.get("complexity", {})
            complexity_level = complexity.get("complexity_level", "").lower()
            if complexity_level:
                issue.add_to_labels(f"complexity-{complexity_level}")
            
            print(f"   ✅ Updated labels for issue #{issue.number}")
            
        except Exception as e:
            print(f"   ⚠️  Could not update labels: {e}")
    
    async def create_story_breakdown_issues(self, parent_issue_data: Dict[str, Any], 
                                          stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create individual GitHub Issues for each story in the breakdown.
        
        This creates a clear task structure that humans can follow.
        
        Args:
            parent_issue_data: The original feature request
            stories: List of story definitions from Projektledare
            
        Returns:
            List of created story issues
        """
        try:
            print(f"📋 Creating {len(stories)} story issues...")
            
            created_issues = []
            parent_issue_number = parent_issue_data["number"]
            
            for story in stories:
                story_issue = await self._create_single_story_issue(
                    story, parent_issue_number
                )
                if story_issue:
                    created_issues.append(story_issue)
            
            # Update parent issue with links to child stories
            await self._update_parent_with_story_links(
                parent_issue_data["github_issue"], created_issues
            )
            
            print(f"✅ Created {len(created_issues)} story issues")
            return created_issues
            
        except Exception as e:
            print(f"❌ Error creating story breakdown: {e}")
            return []

    async def create_story_breakdown_issues_enhanced(self, parent_issue_data: Dict[str, Any], 
                                                stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhanced story creation with development links."""
        enhanced_workflow = EnhancedGitHubWorkflow(self)
        return await enhanced_workflow.create_story_breakdown_with_development_links(
            parent_issue_data, stories
        )

    async def _create_single_story_issue(self, story: Dict[str, Any], 
                                       parent_issue_number: int) -> Optional[Dict[str, Any]]:
        """Create a single GitHub Issue for a story."""
        try:
            # Format story as GitHub Issue
            title = f"[STORY] {story['title']}"
            
            body = f"""## 📋 Story från Feature #{parent_issue_number}

**Story ID**: {story['story_id']}
**Tilldelad Agent**: {story['assigned_agent']}
**Story-typ**: {story['story_type']}
**Estimerad insats**: {story['estimated_effort']}

### 📝 Beskrivning
{story['description']}

### ✅ Acceptanskriterier
"""
            
            for criterion in story['acceptance_criteria']:
                body += f"- [ ] {criterion}\n"
            
            if story.get('dependencies'):
                body += f"\n### 🔗 Beroenden\n"
                for dep in story['dependencies']:
                    body += f"- {dep}\n"
            
            if story.get('design_principles_addressed'):
                body += f"\n### 🎯 Designprinciper som adresseras\n"
                for principle in story['design_principles_addressed']:
                    body += f"- {principle}\n"
            
            body += f"""
### 🤖 AI-Agent Information
**Ansvarig agent**: {story['assigned_agent']}
**Definierad av**: AI Projektledare
**Skapad**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
*Denna story är del av automated workflow för Feature #{parent_issue_number}*
*AI-Team kan börja arbeta på denna när alla beroenden är uppfyllda*
"""
            
            # Create the issue
            new_issue = self.project_repo.create_issue(
                title=title,
                body=body,
                labels=['story', 'ai-generated', f'agent-{story["assigned_agent"]}', 
                       f'effort-{story["estimated_effort"].lower()}']
            )
            
            print(f"   ✅ Created story issue #{new_issue.number}: {story['story_id']}")
            
            return {
                "story_id": story['story_id'],
                "github_issue": new_issue,
                "number": new_issue.number,
                "url": new_issue.html_url,
                "assigned_agent": story['assigned_agent']
            }
            
        except Exception as e:
            print(f"   ❌ Failed to create story issue for {story['story_id']}: {e}")
            return None
    
    async def _update_parent_with_story_links(self, parent_issue: Issue, 
                                            story_issues: List[Dict[str, Any]]):
        """Add comment to parent issue with links to all created stories."""
        try:
            comment_body = f"""## 📋 Story Breakdown Skapad

AI-teamet har skapat {len(story_issues)} implementerings-stories:

"""
            
            for story_issue in story_issues:
                comment_body += f"- #{story_issue['number']}: {story_issue['story_id']} (→ {story_issue['assigned_agent']})\n"
            
            comment_body += f"""
### 🚀 Utvecklingsprocess
Stories kommer att implementeras i följande ordning baserat på beroenden och agent-tillgänglighet.

**Spårning**: Följ länkarna ovan för att se framsteg på varje story.
**Estimerad total tid**: {sum(1 for _ in story_issues)} stories implementeras parallellt/sekventiellt.

---
*Automatisk story-breakdown av AI Projektledare • {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
            
            parent_issue.create_comment(comment_body)
            print(f"   ✅ Updated parent issue #{parent_issue.number} with story links")
            
        except Exception as e:
            print(f"   ⚠️  Could not update parent issue: {e}")


class ProjectOwnerCommunication:
    """
    High-level interface for Projektledare to communicate with project owner via GitHub.
    
    This is the main class that Projektledare uses for all GitHub operations.
    """
    
    def __init__(self):
        self.github = GitHubIntegration()
        self.status_handler = StatusHandler()
    
    async def process_new_features(self) -> List[Dict[str, Any]]:
        """
        Main entry point: Process all new feature requests found on GitHub.
        
        WORKFLOW:
        1. Scan GitHub for new feature requests
        2. For each request, trigger Projektledare analysis
        3. Post analysis results to GitHub
        4. Create story breakdown if approved
        
        Returns:
            List of processed features with their analysis results
        """
        print("🚀 Starting feature request processing...")
        
        # Get new feature requests from GitHub
        new_requests = await self.github.monitor_new_feature_requests()
        
        if not new_requests:
            print("ℹ️  No new feature requests found")
            return []
        
        processed_features = []
        
        for request in new_requests:
            try:
                print(f"\n🔍 Processing #{request['number']}: {request['title']}")
                
                # Import here to avoid circular imports
                from agents.projektledare import create_projektledare
                
                # Create Projektledare and run analysis
                projektledare = create_projektledare()
                analysis = await projektledare.analyze_feature_request(request)
                
                # Post analysis results to GitHub
                posted = await self.github.post_analysis_results(request, analysis)
                
                if posted:
                    print(f"   ✅ Posted analysis to GitHub")
                    
                    # If approved, create story breakdown
                    if analysis.get("recommendation", {}).get("action") == "approve":
                        print(f"   📋 Creating story breakdown...")
                        
                        stories = await projektledare.create_story_breakdown(analysis, request)
                        
                        if stories:
                            story_issues = await self.github.create_story_breakdown_issues(
                                request, stories
                            )
                            print(f"   ✅ Created {len(story_issues)} story issues")

                            # Delegate stories to team automatically
                                print("🎯 Auto-delegating stories to AI team...")
                                delegation_result = await projektledare.delegate_stories_to_team(stories)
                                if delegation_result['coordination_active']:
                                    print(f"✅ Delegated {len(delegation_result['delegated_stories'])} stories to team")
                                else:
                                    print("⚠️  Story delegation failed")

                        else:
                            print(f"   ⚠️  No stories created")
                
                processed_features.append({
                    "request": request,
                    "analysis": analysis,
                    "processed_at": datetime.now().isoformat(),
                    "github_updated": posted
                })
                
            except Exception as e:
                print(f"❌ Failed to process #{request['number']}: {e}")
                report_error("project_owner_communication", "FEATURE_PROCESSING_ERROR", str(e))
        
        print(f"\n🎉 Processed {len(processed_features)} feature requests")
        return processed_features
    
    async def check_for_approvals(self) -> List[Dict[str, Any]]:
        """Check for human approvals/rejections of completed features."""
        # TODO: Implement approval checking
        # This would scan for issues with 'feature-approval' label
        return []
    

        """Enhanced process that includes automatic implementation triggering."""
        
        # Get normal feature processing results
        processed_features = await self.process_new_features()
        
        # Auto-trigger implementation for approved features
        for feature in processed_features:
            if feature.get('github_updated') and feature.get('stories_created', 0) > 0:
                try:
                    # Create auto implementation trigger
                        self.github.projektledare if hasattr(self.github, 'projektledare') else None,
                        self.github
                    )
                    
                    # Get parent issue number
                    parent_issue_number = feature['request']['number']
                    story_issues = feature.get('story_issues', [])
                    
                    # Trigger automatic implementation
                    trigger_result = await auto_trigger.trigger_story_implementation(
                        parent_issue_number, story_issues
                    )
                    
                    print(f"🚀 Auto-implementation triggered for feature #{parent_issue_number}")
                    
                except Exception as e:
                    print(f"⚠️  Auto-implementation trigger failed: {e}")
        
        return processed_features


# Factory function for easy usage
def create_project_owner_communication() -> ProjectOwnerCommunication:
    """Create configured GitHub communication system."""
    return ProjectOwnerCommunication()
