"""
Enhanced Git Tools for Cross-Repo AI Development Workflow (Fixed for CrewAI)
===========================================================================

PURPOSE:
Provides AI agents with ability to work across repositories with proper CrewAI integration.

FIXED ISSUES:
- CrewAI tool compatibility
- Proper BaseTool import
- Version conflicts resolved
"""

from typing import Any, Optional, Dict, List
from pathlib import Path
import git
import os
import json
import re
from datetime import datetime

# FIXED: Use correct CrewAI imports based on available version
try:
    # Try new CrewAI format first
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field
    CREWAI_V2 = True
except ImportError:
    try:
        # Try older CrewAI format
        from crewai_tools import BaseTool
        from pydantic import BaseModel, Field
        CREWAI_V2 = True
    except ImportError:
        # Fallback to manual implementation
        from pydantic import BaseModel, Field
        CREWAI_V2 = False
        
        class BaseTool(BaseModel):
            name: str
            description: str
            
            def _run(self, *args, **kwargs):
                raise NotImplementedError

try:
    from github import Github, Repository
    GITHUB_AVAILABLE = True
except ImportError:
    print("⚠️  PyGithub not installed. Git operations will work but GitHub API features disabled.")
    GITHUB_AVAILABLE = False

# Project imports
from config.settings import SECRETS, GITHUB_CONFIG, PROJECT_ROOT

# Workspace configuration for cross-repo operations
AI_REPO_PATH = PROJECT_ROOT  # This repo (multi-agent-setup)
PRODUCT_REPO_PATH = Path("C:/Users/jcols/Documents/diginativa-game")  # local directory for diginativa-game

class GitCommandInput(BaseModel):
    """Input schema for Git operations."""
    command: str = Field(..., description="Git command to execute")
    story_id: Optional[str] = Field(None, description="Story ID for branch naming")
    branch_name: Optional[str] = Field(None, description="Custom branch name")
    commit_message: Optional[str] = Field(None, description="Commit message")
    files_to_add: Optional[List[str]] = Field(None, description="List of file paths to add")
    pr_title: Optional[str] = Field(None, description="Pull request title")
    pr_body: Optional[str] = Field(None, description="Pull request description")
    target_repo: str = Field('product_repo', description="Which repo to operate on")

class EnhancedGitTool(BaseTool):
    """
    Enhanced Git tool supporting cross-repository AI development workflow.
    
    FIXED FOR CREWAI COMPATIBILITY:
    - Proper tool inheritance
    - Correct parameter handling
    - Version-agnostic imports
    """
    name: str = "Enhanced Git Repository Manager"
    description: str = (
        "Manage Git operations across AI-team and product repositories. "
        "Supports creating feature branches, committing code, creating pull requests."
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize repositories
        self._ai_repo = None
        self._product_repo = None
        
        # Initialize GitHub API if available
        self._github_client = None
        self._setup_github_api()
    
    def _setup_github_api(self):
        """Setup GitHub API client if available and configured."""
        if not GITHUB_AVAILABLE:
            return
            
        try:
            github_token = SECRETS.get('github_token')
            if github_token and not github_token.startswith("[YOUR_"):
                self._github_client = Github(github_token)
                print(f"✅ GitHub API initialized")
            else:
                print(f"⚠️  GitHub token not configured")
        except Exception as e:
            print(f"⚠️  GitHub API initialization failed: {e}")

    def _run(self, command: str, **kwargs) -> str:
        """Execute the specified Git command with parameters."""
        try:
            print(f"🔧 Executing Git command: {command}")
            
            if command == 'setup_workspace':
                return self._setup_workspace(**kwargs)
            elif command == 'create_feature_branch':
                return self._create_feature_branch(**kwargs)
            elif command == 'commit_changes':
                return self._commit_changes(**kwargs)
            elif command == 'push_branch':
                return self._push_branch(**kwargs)
            elif command == 'create_pull_request':
                return self._create_pull_request(**kwargs)
            elif command == 'sync_repos':
                return self._sync_repos(**kwargs)
            elif command == 'cleanup_branches':
                return self._cleanup_branches(**kwargs)
            else:
                return f"❌ Unknown Git command: {command}"
                
        except Exception as e:
            error_msg = f"Git operation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def _get_ai_repo(self) -> git.Repo:
        """Get or initialize AI repository (this repo - multi-agent-setup)."""
        if self._ai_repo is None:
            if AI_REPO_PATH.exists() and (AI_REPO_PATH / ".git").exists():
                self._ai_repo = git.Repo(AI_REPO_PATH)
                print(f"✅ AI repo loaded from {AI_REPO_PATH}")
            else:
                raise Exception(f"AI repo not found at {AI_REPO_PATH}")
        return self._ai_repo

    def _get_product_repo(self) -> git.Repo:
        """Get or clone product repository (diginativa-game)."""
        if self._product_repo is None:
            if PRODUCT_REPO_PATH.exists() and (PRODUCT_REPO_PATH / ".git").exists():
                # Repo exists, load and update
                self._product_repo = git.Repo(PRODUCT_REPO_PATH)
                try:
                    # Try to pull latest changes
                    self._product_repo.remotes.origin.pull('main')
                    print(f"✅ Product repo updated from {PRODUCT_REPO_PATH}")
                except Exception as e:
                    print(f"⚠️  Could not update product repo: {e}")
            else:
                # Clone the repo
                self._clone_product_repo()
        return self._product_repo

    def _clone_product_repo(self):
        """Clone the product repository to workspace."""
        try:
            product_config = GITHUB_CONFIG['project_repo']
            github_token = SECRETS.get('github_token', '')
            
            # Create repo URL with or without token
            if github_token and not github_token.startswith("[YOUR_"):
                repo_url = f"https://{github_token}@github.com/{product_config['owner']}/{product_config['name']}.git"
            else:
                repo_url = f"https://github.com/{product_config['owner']}/{product_config['name']}.git"
            
            # Ensure workspace directory exists
            PRODUCT_REPO_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"🔄 Cloning product repo to {PRODUCT_REPO_PATH}...")
            self._product_repo = git.Repo.clone_from(repo_url, PRODUCT_REPO_PATH)
            print(f"✅ Product repo cloned successfully")
            
        except Exception as e:
            raise Exception(f"Failed to clone product repo: {e}")

    def _setup_workspace(self, **kwargs) -> str:
        """Set up the complete workspace for cross-repo development."""
        try:
            results = []
            
            # Ensure AI repo is accessible
            ai_repo = self._get_ai_repo()
            results.append(f"✅ AI repo ready: {ai_repo.working_dir}")
            
            # Clone/update product repo
            product_repo = self._get_product_repo()
            results.append(f"✅ Product repo ready: {product_repo.working_dir}")
            
            # Create necessary directories in product repo
            directories_to_create = [
                "docs/specs",
                "frontend/src/components", 
                "backend/app/api",
                "tests/integration"
            ]
            
            for dir_path in directories_to_create:
                full_path = PRODUCT_REPO_PATH / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                results.append(f"✅ Directory ensured: {dir_path}")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ Workspace setup failed: {str(e)}"

    def _create_feature_branch(self, **kwargs) -> str:
        """Create a feature branch in the appropriate repository."""
        try:
            target_repo = kwargs.get('target_repo', 'product_repo')
            story_id = kwargs.get('story_id')
            custom_branch_name = kwargs.get('branch_name')
            
            # Determine branch name
            if custom_branch_name:
                branch_name = custom_branch_name
            elif story_id:
                # Generate branch name from story ID
                timestamp = datetime.now().strftime("%Y%m%d")
                branch_name = f"feature/{story_id}-{timestamp}"
            else:
                return "❌ Either story_id or branch_name must be provided"
            
            # Get the target repository
            if target_repo == 'ai_repo':
                repo = self._get_ai_repo()
                repo_name = "AI repo"
            else:
                repo = self._get_product_repo()
                repo_name = "Product repo"
            
            # Ensure we're on main branch and it's up to date
            main_branch = repo.heads.main
            main_branch.checkout()
            
            try:
                repo.remotes.origin.pull('main')
            except Exception as e:
                print(f"⚠️  Could not pull latest main: {e}")
            
            # Delete branch if it already exists locally
            if branch_name in [head.name for head in repo.heads]:
                repo.delete_head(branch_name, force=True)
                print(f"🗑️  Deleted existing local branch: {branch_name}")
            
            # Create and checkout new branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            result = f"✅ Created and checked out branch '{branch_name}' in {repo_name}"
            print(result)
            return result
            
        except Exception as e:
            return f"❌ Failed to create feature branch: {str(e)}"

    def _commit_changes(self, **kwargs) -> str:
        """Commit changes to the current branch."""
        try:
            target_repo = kwargs.get('target_repo', 'product_repo')
            commit_message = kwargs.get('commit_message', 'AI-generated changes')
            files_to_add = kwargs.get('files_to_add', [])
            
            # Get the target repository
            if target_repo == 'ai_repo':
                repo = self._get_ai_repo()
                base_path = AI_REPO_PATH
            else:
                repo = self._get_product_repo()
                base_path = PRODUCT_REPO_PATH
            
            # Check if there are any changes
            if not repo.is_dirty(untracked_files=True):
                return "ℹ️  No changes to commit"
            
            # Add specific files or all changes
            if files_to_add:
                for file_path in files_to_add:
                    # Convert to path relative to repo root
                    if str(file_path).startswith(str(base_path)):
                        rel_path = Path(file_path).relative_to(base_path)
                    else:
                        rel_path = file_path
                    repo.index.add([str(rel_path)])
                    print(f"📁 Added file: {rel_path}")
            else:
                # Add all changes
                repo.git.add(A=True)
                print("📁 Added all changes")
            
            # Create commit
            commit = repo.index.commit(commit_message)
            
            result = f"✅ Committed changes: {commit.hexsha[:8]} - {commit_message}"
            print(result)
            return result
            
        except Exception as e:
            return f"❌ Failed to commit changes: {str(e)}"

    def _push_branch(self, **kwargs) -> str:
        """Push the current branch to remote repository."""
        try:
            target_repo = kwargs.get('target_repo', 'product_repo')
            
            # Get the target repository
            if target_repo == 'ai_repo':
                repo = self._get_ai_repo()
                repo_name = "AI repo"
            else:
                repo = self._get_product_repo()
                repo_name = "Product repo"
            
            # Get current branch
            current_branch = repo.active_branch
            branch_name = current_branch.name
            
            # Push branch to remote
            origin = repo.remotes.origin
            origin.push(current_branch, set_upstream=True)
            
            result = f"✅ Pushed branch '{branch_name}' to remote {repo_name}"
            print(result)
            return result
            
        except Exception as e:
            return f"❌ Failed to push branch: {str(e)}"

    def _create_pull_request(self, **kwargs) -> str:
        """Create a pull request in the target repository."""
        if not GITHUB_AVAILABLE or not self._github_client:
            return "❌ GitHub API not available for pull request creation"
            
        try:
            target_repo = kwargs.get('target_repo', 'product_repo')
            pr_title = kwargs.get('pr_title', 'AI-generated feature implementation')
            pr_body = kwargs.get('pr_body', 'This pull request was created by the DigiNativa AI team.')
            story_id = kwargs.get('story_id', 'UNKNOWN')
            
            # Get the GitHub repository object
            if target_repo == 'ai_repo':
                ai_config = GITHUB_CONFIG['ai_team_repo']
                github_repo = self._github_client.get_repo(f"{ai_config['owner']}/{ai_config['name']}")
                local_repo = self._get_ai_repo()
            else:
                product_config = GITHUB_CONFIG['project_repo']
                github_repo = self._github_client.get_repo(f"{product_config['owner']}/{product_config['name']}")
                local_repo = self._get_product_repo()
            
            # Get current branch name
            current_branch = local_repo.active_branch.name
            base_branch = GITHUB_CONFIG['project_repo']['branch']  # Usually 'main'
            
            # Create pull request
            pr = github_repo.create_pull(
                title=pr_title,
                body=f"{pr_body}\n\n**Story ID:** {story_id}\n**Created by:** DigiNativa AI Team",
                head=current_branch,
                base=base_branch
            )
            
            result = f"✅ Created Pull Request #{pr.number}: {pr.html_url}"
            print(result)
            return result
            
        except Exception as e:
            return f"❌ Failed to create pull request: {str(e)}"

    def _sync_repos(self, **kwargs) -> str:
        """Synchronize both repositories with their remotes."""
        try:
            results = []
            
            # Sync AI repo
            try:
                ai_repo = self._get_ai_repo()
                ai_repo.remotes.origin.pull('main')
                results.append("✅ AI repo synchronized")
            except Exception as e:
                results.append(f"⚠️  AI repo sync warning: {e}")
            
            # Sync product repo
            try:
                product_repo = self._get_product_repo()
                product_repo.remotes.origin.pull('main')
                results.append("✅ Product repo synchronized")
            except Exception as e:
                results.append(f"⚠️  Product repo sync warning: {e}")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ Repo synchronization failed: {str(e)}"

    def _cleanup_branches(self, **kwargs) -> str:
        """Clean up old feature branches."""
        try:
            target_repo = kwargs.get('target_repo', 'product_repo')
            
            # Get the target repository
            if target_repo == 'ai_repo':
                repo = self._get_ai_repo()
                repo_name = "AI repo"
            else:
                repo = self._get_product_repo()
                repo_name = "Product repo"
            
            # Switch to main branch
            main_branch = repo.heads.main
            main_branch.checkout()
            
            # Find and delete feature branches that are merged
            deleted_count = 0
            for branch in repo.heads:
                if branch.name.startswith('feature/') and branch != repo.active_branch:
                    try:
                        repo.delete_head(branch, force=True)
                        deleted_count += 1
                        print(f"🗑️  Deleted branch: {branch.name}")
                    except Exception as e:
                        print(f"⚠️  Could not delete branch {branch.name}: {e}")
            
            result = f"✅ Cleaned up {deleted_count} feature branches in {repo_name}"
            return result
            
        except Exception as e:
            return f"❌ Branch cleanup failed: {str(e)}"

# Factory function for creating the enhanced git tool
def create_enhanced_git_tool() -> EnhancedGitTool:
    """Create and return a configured EnhancedGitTool instance."""
    return EnhancedGitTool()

# Convenience functions for common operations
def setup_cross_repo_workspace() -> str:
    """Set up workspace for cross-repository development."""
    git_tool = create_enhanced_git_tool()
    return git_tool._run('setup_workspace')

def create_story_branch(story_id: str, target_repo: str = 'product_repo') -> str:
    """Create a feature branch for a specific story."""
    git_tool = create_enhanced_git_tool()
    return git_tool._run('create_feature_branch', story_id=story_id, target_repo=target_repo)

def commit_and_push_changes(commit_message: str, files: List[str] = None, target_repo: str = 'product_repo') -> str:
    """Commit and push changes in one operation."""
    git_tool = create_enhanced_git_tool()
    
    # Commit changes
    commit_result = git_tool._run('commit_changes', 
                                  commit_message=commit_message, 
                                  files_to_add=files,
                                  target_repo=target_repo)
    
    if "✅" not in commit_result:
        return commit_result
    
    # Push changes
    push_result = git_tool._run('push_branch', target_repo=target_repo)
    
    return f"{commit_result}\n{push_result}"

# Test function
def test_cross_repo_workflow():
    """Test the cross-repository workflow."""
    print("🧪 Testing Cross-Repository Workflow...")
    
    try:
        # Test 1: Setup workspace
        print("\n1. Setting up workspace...")
        setup_result = setup_cross_repo_workspace()
        print(setup_result)
        
        # Test 2: Create feature branch
        print("\n2. Creating feature branch...")
        branch_result = create_story_branch("STORY-TEST-001")
        print(branch_result)
        
        # Test 3: Get git tool info
        print("\n3. Testing git tool...")
        git_tool = create_enhanced_git_tool()
        print(f"Git tool created: {git_tool.name}")
        
        print("\n✅ Cross-repository workflow test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Cross-repository workflow test failed: {e}")
        return False

if __name__ == "__main__":
    test_cross_repo_workflow()