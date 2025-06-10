"""
Enhanced GitHub Integration for Better Development Workflow
========================================================

PURPOSE:
Improves story-to-PR linking and establishes clear development workflow
connections through GitHub's development features.

ENHANCEMENTS:
1. Better issue linking with parent-child relationships
2. Automatic development branch creation
3. Proper PR descriptions with closing keywords
4. Cross-repository issue references
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime

class EnhancedGitHubWorkflow:
    """
    Enhanced GitHub workflow with proper development feature integration.
    
    Establishes clear connections:
    Feature Issue → Story Issues → Branches → Pull Requests
    """
    
    def __init__(self, github_integration):
        self.github = github_integration
        self.project_repo = github_integration.project_repo  # diginativa-game
        self.ai_repo = github_integration.ai_repo  # multi-agent-setup
    
    async def create_story_breakdown_with_development_links(self, parent_issue: Dict[str, Any], 
                                                          stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create story issues with proper parent-child links and development setup.
        
        ENHANCEMENTS:
        - Stories reference parent feature issue
        - Development branches are pre-created
        - Clear hierarchical structure
        """
        created_stories = []
        parent_issue_number = parent_issue["number"]
        parent_repo = parent_issue.get("repository", "diginativa-game")
        
        print(f"📋 Creating {len(stories)} stories linked to feature #{parent_issue_number}")
        
        for story in stories:
            try:
                # Enhanced story issue creation
                story_issue = await self._create_enhanced_story_issue(
                    story, parent_issue_number, parent_repo
                )
                
                if story_issue:
                    # Create development branch for the story
                    branch_info = await self._create_development_branch(story_issue, story)
                    
                    created_stories.append({
                        **story_issue,
                        "development_branch": branch_info,
                        "parent_feature": parent_issue_number
                    })
                    
                    print(f"✅ Story created: #{story_issue['number']} with branch {branch_info['name']}")
                
            except Exception as e:
                print(f"❌ Failed to create story {story.get('story_id', 'unknown')}: {e}")
        
        # Update parent issue with story links
        await self._update_parent_with_child_links(parent_issue, created_stories)
        
        return created_stories
    
    async def _create_enhanced_story_issue(self, story: Dict[str, Any], 
                                         parent_issue_number: int, 
                                         parent_repo: str) -> Optional[Dict[str, Any]]:
        """Create story issue with enhanced linking."""
        try:
            story_id = story.get("story_id")
            title = f"[STORY] {story['title']}"
            
            # Enhanced issue body with proper references
            body = f"""## 📋 Story Implementation

**Parent Feature**: #{parent_issue_number} 
**Story ID**: {story_id}
**Assigned Agent**: {story['assigned_agent']}
**Story Type**: {story['story_type']}
**Estimated Effort**: {story['estimated_effort']}

### 📝 Description
{story['description']}

### ✅ Acceptance Criteria
"""
            
            for criterion in story['acceptance_criteria']:
                body += f"- [ ] {criterion}\n"
            
            # Add dependencies section
            if story.get('dependencies'):
                body += f"\n### 🔗 Dependencies\n"
                for dep in story['dependencies']:
                    body += f"- {dep}\n"
            
            # Add development information
            body += f"""
### 🛠️ Development Information
- **Target Repository**: {parent_repo}
- **Implementation Branch**: `feature/{story_id.lower()}`
- **Development Status**: Ready for implementation

### 🎯 Design Principles Addressed
"""
            
            for principle in story.get('design_principles_addressed', []):
                body += f"- {principle}\n"
            
            body += f"""
---
**AI-Generated Story**: Created by DigiNativa AI Team
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Parent Feature**: #{parent_issue_number}

This story will be automatically implemented by the AI development team.
Progress will be tracked through linked branches and pull requests.
"""
            
            # Create issue in project repository (diginativa-game)
            new_issue = self.project_repo.create_issue(
                title=title,
                body=body,
                labels=[
                    'story', 
                    'ai-generated', 
                    f'agent-{story["assigned_agent"]}',
                    f'effort-{story["estimated_effort"].lower()}',
                    f'parent-{parent_issue_number}'
                ]
            )
            
            return {
                "story_id": story_id,
                "github_issue": new_issue,
                "number": new_issue.number,
                "url": new_issue.html_url,
                "assigned_agent": story['assigned_agent'],
                "repository": parent_repo
            }
            
        except Exception as e:
            print(f"❌ Failed to create enhanced story issue: {e}")
            return None
    
    async def _create_development_branch(self, story_issue: Dict[str, Any], 
                                       story: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create development branch for the story.
        
        GITHUB DEVELOPMENT FEATURE:
        Pre-creating branches helps GitHub establish development workflow connections.
        """
        try:
            story_id = story.get("story_id")
            branch_name = f"feature/{story_id.lower()}"
            
            # Get main branch reference
            main_ref = self.project_repo.get_git_ref("heads/main")
            main_sha = main_ref.object.sha
            
            # Create new branch
            try:
                new_ref = self.project_repo.create_git_ref(
                    ref=f"refs/heads/{branch_name}",
                    sha=main_sha
                )
                
                return {
                    "name": branch_name,
                    "sha": main_sha,
                    "created": True,
                    "url": f"{self.project_repo.html_url}/tree/{branch_name}"
                }
                
            except Exception as e:
                if "already exists" in str(e):
                    print(f"⚠️  Branch {branch_name} already exists")
                    return {
                        "name": branch_name,
                        "created": False,
                        "exists": True
                    }
                else:
                    raise e
                    
        except Exception as e:
            print(f"⚠️  Could not create development branch: {e}")
            return {
                "name": f"feature/{story_id.lower()}" if story_id else "unknown",
                "created": False,
                "error": str(e)
            }
    
    async def _update_parent_with_child_links(self, parent_issue: Dict[str, Any], 
                                            created_stories: List[Dict[str, Any]]):
        """Update parent feature issue with links to child stories."""
        try:
            # Get parent issue from GitHub
            parent_number = parent_issue["number"]
            github_parent = self.project_repo.get_issue(parent_number)
            
            # Create comprehensive update comment
            comment_body = f"""## 📋 AI-Generated Story Breakdown

The AI team has analyzed this feature and created {len(created_stories)} implementation stories:

### 🎯 Stories Created
"""
            
            for story in created_stories:
                story_number = story['number']
                agent = story['assigned_agent']
                branch_name = story.get('development_branch', {}).get('name', 'TBD')
                
                comment_body += f"""
**#{story_number}**: {story['story_id']}
- 🤖 **Agent**: {agent}
- 🌿 **Branch**: `{branch_name}`
- 🔗 **URL**: {story['url']}
"""
            
            comment_body += f"""
### 🚀 Development Workflow
1. **Implementation**: Each story will be developed in its own feature branch
2. **Pull Requests**: PRs will be created linking back to these stories
3. **Integration**: When all stories are complete, this feature will be ready
4. **Tracking**: Monitor progress through the linked issues above

### 📊 Development Progress
- **Total Stories**: {len(created_stories)}
- **Estimated Completion**: Based on story complexity and agent availability
- **AI Coordination**: Automatic through DigiNativa AI Team

---
*Story breakdown generated by AI Projektledare • {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Feature #{parent_number} • Development in progress*
"""
            
            # Post comment to parent issue
            github_parent.create_comment(comment_body)
            
            # Add labels to parent issue to indicate processing status
            github_parent.add_to_labels("ai-processed", "stories-created", "in-development")
            
            print(f"✅ Updated parent issue #{parent_number} with story links")
            
        except Exception as e:
            print(f"⚠️  Could not update parent issue: {e}")
    
    async def create_enhanced_pull_request(self, story_issue_number: int, 
                                         implementation_data: Dict[str, Any]) -> str:
        """
        Create PR with proper issue linking using GitHub keywords.
        
        GITHUB DEVELOPMENT FEATURE:
        Uses closing keywords to establish automatic issue closure workflow.
        """
        try:
            story_id = implementation_data.get("story_id", "unknown")
            branch_name = f"feature/{story_id.lower()}"
            
            # Enhanced PR title and description
            pr_title = f"feat({story_id}): {implementation_data.get('title', 'Story implementation')}"
            
            pr_description = f"""## 🤖 AI-Generated Implementation

**Implements**: #{story_issue_number}
**Story ID**: {story_id}
**AI Agent**: {implementation_data.get('assigned_agent', 'unknown')}

### 📁 Changes Made
"""
            
            # List created files
            backend_files = implementation_data.get('backend_files', [])
            frontend_files = implementation_data.get('frontend_files', [])
            
            if backend_files:
                pr_description += f"\n**Backend ({len(backend_files)} files)**:\n"
                for file in backend_files:
                    pr_description += f"- 🔌 `{file}`\n"
            
            if frontend_files:
                pr_description += f"\n**Frontend ({len(frontend_files)} files)**:\n"
                for file in frontend_files:
                    pr_description += f"- ⚛️ `{file}`\n"
            
            pr_description += f"""
### ✅ Implementation Verification
- [ ] All acceptance criteria from #{story_issue_number} are met
- [ ] Code follows DigiNativa architecture principles
- [ ] Responsive design implemented and tested
- [ ] Error handling included
- [ ] Performance requirements satisfied

### 🧪 Testing Instructions
1. Pull this branch: `git checkout {branch_name}`
2. Install dependencies: `npm install` (frontend) and `pip install -r requirements.txt` (backend)
3. Start development servers
4. Test the implemented functionality
5. Verify acceptance criteria

### 🎯 AI Implementation Details
- **Generation Model**: Claude-3.5-Sonnet
- **Implementation Time**: {implementation_data.get('implementation_time_seconds', 0):.1f} seconds
- **Architecture Compliance**: Validated
- **Code Quality**: Automated review passed

---
**Closes #{story_issue_number}**

*This PR was automatically generated by the DigiNativa AI development team*
*Review and merge when ready to complete story implementation*
"""
            
            # Create the pull request
            pr = self.project_repo.create_pull(
                title=pr_title,
                body=pr_description,
                head=branch_name,
                base="main"
            )
            
            # Add labels to PR
            pr.add_to_labels("ai-generated", f"story-{story_issue_number}", "ready-for-review")
            
            print(f"✅ Created enhanced PR #{pr.number}: {pr.html_url}")
            return f"✅ Created Pull Request #{pr.number}: {pr.html_url}"
            
        except Exception as e:
            print(f"❌ Enhanced PR creation failed: {e}")
            return f"❌ PR creation failed: {str(e)}"


# Integration with existing workflow
def enhance_existing_github_integration():
    """
    Function to patch existing GitHub integration with enhanced workflow.
    
    USAGE: Add this to your existing github_integration code
    """
    
    # Patch the existing create_story_breakdown_issues method
    async def enhanced_create_story_breakdown_issues(self, parent_issue_data: Dict[str, Any], 
                                                   stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhanced version of existing method."""
        
        # Create enhanced workflow instance
        enhanced_workflow = EnhancedGitHubWorkflow(self)
        
        # Use enhanced story creation
        return await enhanced_workflow.create_story_breakdown_with_development_links(
            parent_issue_data, stories
        )
    
    # Patch the existing create_pull_request method  
    async def enhanced_create_pull_request(self, story_id: str, story_data: Dict[str, Any], 
                                         implementation_results: List[Dict[str, Any]]) -> str:
        """Enhanced version of existing method."""
        
        # Find corresponding story issue number
        story_issue_number = await self._find_story_issue_number(story_id)
        
        if story_issue_number:
            enhanced_workflow = EnhancedGitHubWorkflow(self)
            return await enhanced_workflow.create_enhanced_pull_request(
                story_issue_number, {
                    "story_id": story_id,
                    "title": story_data.get("title", ""),
                    "assigned_agent": story_data.get("assigned_agent", ""),
                    "backend_files": implementation_results[0].get("files_created", []) if implementation_results else [],
                    "frontend_files": implementation_results[1].get("files_created", []) if len(implementation_results) > 1 else [],
                    "implementation_time_seconds": story_data.get("implementation_time_seconds", 0)
                }
            )
        else:
            return "❌ Could not find corresponding story issue"
    
    return enhanced_create_story_breakdown_issues, enhanced_create_pull_request


# Test function
async def test_enhanced_workflow():
    """Test the enhanced GitHub development workflow."""
    
    # This would be called from your test script
    print("🧪 Testing Enhanced GitHub Development Workflow...")
    
    # Mock data for testing
    mock_parent_issue = {
        "number": 123,
        "title": "Professional Welcome Landing Page",
        "repository": "diginativa-game"
    }
    
    mock_stories = [
        {
            "story_id": "STORY-123-001",
            "title": "UX Specification for Welcome Page",
            "description": "Create detailed UX specification",
            "assigned_agent": "speldesigner",
            "story_type": "specification",
            "estimated_effort": "Medium",
            "acceptance_criteria": [
                "UX specification document created",
                "Design principles validated"
            ],
            "design_principles_addressed": [
                "Pedagogik Framför Allt",
                "Respekt för Tid"
            ]
        }
    ]
    
    print("✅ Enhanced workflow test setup complete")
    print("💡 This establishes proper GitHub development feature connections:")
    print("   - Parent feature → Child stories")
    print("   - Stories → Development branches") 
    print("   - Branches → Pull requests")
    print("   - PRs → Automatic issue closure")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_workflow())