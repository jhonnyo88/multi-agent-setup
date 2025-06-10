"""
Automatic Story Implementation Trigger
====================================

PURPOSE:
Automatically triggers implementation of created stories through the AI team.
Bridges the gap between story creation and actual code generation.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any
import time

class AutoImplementationTrigger:
    """
    Automatically triggers implementation when stories are created.
    
    WORKFLOW:
    1. Detect when new stories are created
    2. Wait brief period for GitHub to process
    3. Delegate stories to appropriate agents
    4. Monitor implementation progress
    """
    
    def __init__(self, projektledare_agent, github_integration):
        self.projektledare = projektledare_agent
        self.github = github_integration
        self.implementation_delays = {
            "speldesigner": 2,     # UX specs can start immediately
            "utvecklare": 5,       # Wait for specs to be ready
            "testutvecklare": 10,  # Wait for code to be implemented
            "qa_testare": 15,      # Wait for tests to be written
            "kvalitetsgranskare": 20  # Final quality review
        }
    
    async def trigger_story_implementation(self, parent_issue_number: int, 
                                         created_stories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Automatically trigger implementation of newly created stories.
        
        Args:
            parent_issue_number: The parent feature issue number
            created_stories: List of created story GitHub issues
            
        Returns:
            Implementation trigger results
        """
        try:
            print(f"🚀 Auto-triggering implementation for {len(created_stories)} stories...")
            
            # Convert GitHub issues to story format for delegation
            story_data_list = await self._convert_issues_to_story_data(created_stories)
            
            if not story_data_list:
                return {
                    "success": False,
                    "error": "No valid stories to implement",
                    "stories_processed": 0
                }
            
            # Delegate stories to AI team coordinator
            delegation_result = await self._delegate_stories_with_timing(story_data_list)
            
            # Start progress monitoring
            if delegation_result.get('coordination_active'):
                asyncio.create_task(self._monitor_implementation_progress(parent_issue_number))
            
            return {
                "success": True,
                "stories_processed": len(story_data_list),
                "delegation_result": delegation_result,
                "parent_issue": parent_issue_number,
                "triggered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Auto-implementation trigger failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "stories_processed": 0
            }
    
    async def _convert_issues_to_story_data(self, github_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert GitHub issue data to story format for delegation."""
        story_data_list = []
        
        for github_issue in github_issues:
            try:
                # Extract story information from GitHub issue
                issue_number = github_issue.get('number')
                story_id = github_issue.get('story_id', f"STORY-{issue_number}")
                
                # Get full issue details from GitHub
                full_issue = self.github.project_repo.get_issue(issue_number)
                
                # Parse story data from issue body
                story_data = await self._parse_story_from_issue(full_issue, story_id)
                story_data_list.append(story_data)
                
                print(f"   📄 Prepared {story_id} for delegation")
                
            except Exception as e:
                print(f"   ⚠️  Could not prepare story from issue #{github_issue.get('number', 'unknown')}: {e}")
        
        return story_data_list
    
    async def _parse_story_from_issue(self, github_issue, story_id: str) -> Dict[str, Any]:
        """Parse story data from GitHub issue content."""
        
        # Extract assigned agent from labels or content
        assigned_agent = "entwicklare"  # Default
        for label in github_issue.labels:
            if label.name.startswith('agent-'):
                assigned_agent = label.name.replace('agent-', '')
                break
        
        # Extract story type from title or content
        title = github_issue.title.replace("[STORY] ", "")
        
        if "UX Specification" in title:
            story_type = "specification"
            assigned_agent = "speldesigner"
        elif "Backend API" in title:
            story_type = "backend"
            assigned_agent = "utvecklare"
        elif "React Component" in title:
            story_type = "frontend"
            assigned_agent = "utvecklare"
        elif "Automated Tests" in title:
            story_type = "testing"
            assigned_agent = "testutvecklare"
        elif "QA Testing" in title:
            story_type = "qa"
            assigned_agent = "qa_testare"
        else:
            story_type = "full_feature"
            assigned_agent = "utvecklare"
        
        # Extract acceptance criteria from issue body
        acceptance_criteria = self._extract_acceptance_criteria(github_issue.body or "")
        
        return {
            "story_id": story_id,
            "title": title,
            "description": github_issue.body[:200] + "..." if github_issue.body else f"Implementation of {title}",
            "story_type": story_type,
            "assigned_agent": assigned_agent,
            "acceptance_criteria": acceptance_criteria or [
                "Implementation completed according to specification",
                "Code follows architecture principles",
                "All tests pass"
            ],
            "estimated_effort": "Medium",
            "user_value": "Professional functionality for Anna",
            "design_principles_addressed": ["Pedagogik Framför Allt", "Respekt för Tid"],
            "github_issue_number": github_issue.number,
            "github_url": github_issue.html_url
        }
    
    def _extract_acceptance_criteria(self, issue_body: str) -> List[str]:
        """Extract acceptance criteria from issue body."""
        criteria = []
        
        # Look for acceptance criteria section
        import re
        criteria_match = re.search(r'### ✅ Acceptance Criteria\s*\n(.*?)(?=\n###|\n\n---|\Z)', issue_body, re.DOTALL)
        
        if criteria_match:
            criteria_text = criteria_match.group(1)
            # Extract bullet points
            criteria_lines = re.findall(r'^\s*[-*]\s*\[\s*\]\s*(.+)$', criteria_text, re.MULTILINE)
            criteria.extend(criteria_lines)
        
        return criteria
    
    async def _delegate_stories_with_timing(self, story_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Delegate stories with appropriate timing based on dependencies."""
        
        if not self.projektledare.agent_coordinator:
            print("⚠️  Agent coordinator not available")
            return {"coordination_active": False, "delegated_stories": []}
        
        # Sort stories by agent priority (specs first, then implementation, then testing)
        agent_priority = {
            "speldesigner": 1,
            "utvecklare": 2,
            "testutvecklare": 3,
            "qa_testare": 4,
            "kvalitetsgranskare": 5
        }
        
        sorted_stories = sorted(story_data_list, key=lambda s: agent_priority.get(s['assigned_agent'], 99))
        
        delegation_results = []
        
        for story_data in sorted_stories:
            try:
                agent_name = story_data['assigned_agent']
                delay = self.implementation_delays.get(agent_name, 0)
                
                if delay > 0:
                    print(f"   ⏳ Waiting {delay}s before delegating to {agent_name}...")
                    await asyncio.sleep(delay)
                
                # Delegate story to coordinator
                await self.projektledare.agent_coordinator.delegate_story(story_data)
                
                delegation_results.append({
                    "story_id": story_data['story_id'],
                    "delegated_at": datetime.now().isoformat(),
                    "agent": agent_name
                })
                
                print(f"   ✅ Delegated {story_data['story_id']} to {agent_name}")
                
            except Exception as e:
                print(f"   ❌ Failed to delegate {story_data.get('story_id', 'unknown')}: {e}")
        
        return {
            "coordination_active": True,
            "delegated_stories": delegation_results,
            "total_delegated": len(delegation_results)
        }
    
    async def _monitor_implementation_progress(self, parent_issue_number: int):
        """Monitor implementation progress and update parent issue."""
        
        print(f"📊 Starting progress monitoring for feature #{parent_issue_number}")
        
        try:
            # Monitor for 10 minutes maximum
            for _ in range(60):  # 60 * 10s = 10 minutes
                await asyncio.sleep(10)
                
                # Get current team status
                if self.projektledare.agent_coordinator:
                    team_status = self.projektledare.agent_coordinator.get_team_status()
                    
                    active_stories = team_status.get('active_stories', 0)
                    completed_stories = team_status.get('completed_stories', 0)
                    
                    if active_stories > 0 or completed_stories > 0:
                        print(f"📈 Progress update: {active_stories} active, {completed_stories} completed")
                        
                        # Update parent issue every few minutes
                        if (_ % 6) == 0:  # Every minute
                            await self._update_parent_issue_progress(parent_issue_number, team_status)
                    
                    # Stop monitoring if all stories are complete
                    if active_stories == 0 and completed_stories > 0:
                        print(f"🎉 All stories completed for feature #{parent_issue_number}")
                        await self._update_parent_issue_completion(parent_issue_number)
                        break
                else:
                    print("⚠️  Agent coordinator not available for monitoring")
                    break
            
        except Exception as e:
            print(f"⚠️  Progress monitoring error: {e}")
    
    async def _update_parent_issue_progress(self, issue_number: int, team_status: Dict[str, Any]):
        """Update parent issue with progress information."""
        try:
            parent_issue = self.github.project_repo.get_issue(issue_number)
            
            progress_comment = f"""## 🔄 Implementation Progress Update

**Team Status** (Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')})
- **Active Stories**: {team_status.get('active_stories', 0)}
- **Completed Stories**: {team_status.get('completed_stories', 0)}
- **Queued Tasks**: {team_status.get('queued_tasks', 0)}

**Development Health**: {team_status.get('coordination_health', 'unknown')}

*Automatic progress update from DigiNativa AI Team*
"""
            
            parent_issue.create_comment(progress_comment)
            
        except Exception as e:
            print(f"⚠️  Could not update parent issue progress: {e}")
    
    async def _update_parent_issue_completion(self, issue_number: int):
        """Update parent issue when all stories are completed."""
        try:
            parent_issue = self.github.project_repo.get_issue(issue_number)
            
            completion_comment = f"""## ✅ Feature Implementation Completed!

**Status**: All AI-generated stories have been completed and are ready for review.

**Next Steps**:
1. Review the generated Pull Requests
2. Test the implemented functionality
3. Merge approved PRs
4. Close this feature issue when satisfied

**Implementation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

*Feature implementation completed by DigiNativa AI Team*
"""
            
            parent_issue.create_comment(completion_comment)
            parent_issue.add_to_labels("ai-completed", "ready-for-review")
            
        except Exception as e:
            print(f"⚠️  Could not update parent issue completion: {e}")


# Integration function
def create_auto_implementation_trigger(projektledare_agent, github_integration):
    """Factory function to create auto implementation trigger."""
    return AutoImplementationTrigger(projektledare_agent, github_integration)


# Test function
async def test_auto_implementation():
    """Test automatic implementation triggering."""
    print("🧪 Testing Automatic Implementation Trigger...")
    
    # This would be integrated into the main workflow
    print("✅ Auto implementation trigger ready")
    print("💡 Will automatically delegate stories when they are created")
    print("📊 Will monitor progress and update parent issues")
    

if __name__ == "__main__":
    asyncio.run(test_auto_implementation())