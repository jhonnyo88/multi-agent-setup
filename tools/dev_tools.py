"""
Enhanced Git Tools for Cross-Repo AI Development Workflow
========================================================

PURPOSE:
Provides AI agents with ability to work across repositories:
- AI-team repo (multi-agent-setup): Issue monitoring, analysis, coordination
- Product repo (diginativa-game): Code generation, spec creation, deployment

WORKFLOW:
1. GitHub Issues → AI-team repo (multi-agent-setup)
2. Code Generation → Product repo (diginativa-game) 
3. Git Operations → Product repo with proper branching
4. Pull Requests → Product repo for project owner review

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update GITHUB_CONFIG in config/settings.py with your repo names
2. Modify workspace path structure as needed
3. Adjust branch naming conventions
4. Update commit message formats
"""

from typing import Type, Literal, Any, Optional, Dict
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from pathlib import Path
import git
import os
from github import Github, Repository
from datetime import datetime

# Project imports
from config.settings import SECRETS, GITHUB_CONFIG, PROJECT_ROOT

# Workspace configuration for cross-repo operations
AI_REPO_PATH = PROJECT_ROOT  # This repo (multi-agent-setup)
PRODUCT_REPO_PATH = PROJECT_ROOT / "workspace" / GITHUB_CONFIG['project_repo']['name']  # diginativa-game

class GitCommandInput(BaseModel):
    """Input schema for Git operations."""
    command: Literal[
        'setup_workspace', 'create_feature_branch', 'commit_changes', 
        'push_branch', 'create_pull_request', 'sync_repos', 'cleanup_branches'
    ] = Field(..., description="Git command to execute")
    
    # Branch and commit parameters
    story_id: Optional[str] = Field(None, description="Story ID for branch naming (e.g., STORY-123-001)")
    branch_name: Optional[str] = Field(None, description="Custom branch name (overrides story_id)")
    commit_message: Optional[str] = Field(None, description="Commit message")
    
    # File parameters
    files_to_add: Optional[list] = Field(None, description="List of file paths to add to commit")
    
    # Pull request parameters
    pr_title: Optional[str] = Field(None, description="Pull request title")
    pr_body: Optional[str] = Field(None, description="Pull request description")
    
    # Repository selection
    target_repo: Literal['ai_repo', 'product_repo'] = Field('product_repo', description="Which repo to operate on")

class EnhancedGitTool(BaseTool):
    """
    Enhanced Git tool supporting cross-repository AI development workflow.
    
    REPOSITORY ROLES:
    - AI Repo (multi-agent-setup): Issue analysis, agent coordination, status tracking
    - Product Repo (diginativa-game): Code generation, specs, actual product development
    
    WORKFLOW INTEGRATION:
    1. Issues are created in AI repo
    2. Projektledare analyzes and creates stories  
    3. Agents generate code in product repo workspace
    4. Git operations create branches, commits, PRs in product repo
    5. Project owner reviews PRs in product repo
    """
    name: str = "Enhanced Git Repository Manager"
    description: str = (
        "Manage Git operations across AI-team and product repositories. "
        "Supports creating feature branches, committing code, creating pull requests, "
        "and maintaining proper workflow separation between repos."
    )
    args_schema: Type[BaseModel] = GitCommandInput
    
    # Private attributes to avoid Pydantic validation issues
    _ai_repo: Any = PrivateAttr(default=None)
    _product_repo: Any = PrivateAttr(default=None)
    _github_client: Any = PrivateAttr(default=None)
    _ai_github_repo: Any = PrivateAttr(default=None)
    _product_github_repo: Any = PrivateAttr(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize GitHub API client
        try:
            self._github_client = Github(SECRETS['github_token'])
            
            # Get GitHub repo objects
            ai_config = GITHUB_CONFIG['ai_team_repo']
            product_config = GITHUB_CONFIG['project_repo']
            
            self._ai_github_repo = self._github_client.get_repo(f"{ai_config['owner']}/{ai_config['name']}")
            self._product_github_repo = self._github_client.get_repo(f"{product_config['owner']}/{product_config['name']}")
            
            print(f"✅ GitHub API initialized:")
            print(f"   AI Repo: {ai_config['owner']}/{ai_config['name']}")
            print(f"   Product Repo: {product_config['owner']}/{product_config['name']}")
            
        except Exception as e:
            print(f"❌ GitHub API initialization failed: {e}")
            self._github_client = None

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
            repo_url = f"https://{SECRETS['github_token']}@github.com/{product_config['owner']}/{product_config['name']}.git"
            
            # Ensure workspace directory exists
            PRODUCT_REPO_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"🔄 Cloning product repo to {PRODUCT_REPO_PATH}...")
            self._product_repo = git.Repo.clone_from(repo_url, PRODUCT_REPO_PATH)
            print(f"✅ Product repo cloned successfully")
            
        except Exception as e:
            raise Exception(f"Failed to clone product repo: {e}")

    def _run(self, command: str, **kwargs) -> str:
        """Execute the specified Git command."""
        try:
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
            
            # Verify GitHub API access
            if self._github_client:
                ai_repo_info = self._ai_github_repo.name
                product_repo_info = self._product_github_repo.name
                results.append(f"✅ GitHub API access verified for {ai_repo_info} and {product_repo_info}")
            
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
            repo.remotes.origin.pull('main')
            
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
        try:
            target_repo = kwargs.get('target_repo', 'product_repo')
            pr_title = kwargs.get('pr_title', 'AI-generated feature implementation')
            pr_body = kwargs.get('pr_body', 'This pull request was created by the DigiNativa AI team.')
            story_id = kwargs.get('story_id', 'UNKNOWN')
            
            # Get the GitHub repository object
            if target_repo == 'ai_repo':
                github_repo = self._ai_github_repo
                local_repo = self._get_ai_repo()
            else:
                github_repo = self._product_github_repo
                local_repo = self._get_product_repo()
            
            if not github_repo:
                return "❌ GitHub API not available"
            
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
            
            # Find merged feature branches
            merged_branches = []
            for branch in repo.heads:
                if branch.name.startswith('feature/') and branch != repo.active_branch:
                    # Check if branch is merged (simplified check)
                    try:
                        # If we can fast-forward merge, the branch is already merged
                        repo.git.merge_base('--is-ancestor', branch.name, 'main')
                        merged_branches.append(branch)
                    except:
                        # Branch is not merged, keep it
                        pass
            
            # Delete merged branches
            deleted_count = 0
            for branch in merged_branches:
                try:
                    repo.delete_head(branch, force=True)
                    deleted_count += 1
                    print(f"🗑️  Deleted merged branch: {branch.name}")
                except Exception as e:
                    print(f"⚠️  Could not delete branch {branch.name}: {e}")
            
            result = f"✅ Cleaned up {deleted_count} merged branches in {repo_name}"
            return result
            
        except Exception as e:
            return f"❌ Branch cleanup failed: {str(e)}"

    def get_current_branch_info(self, target_repo: str = 'product_repo') -> Dict[str, Any]:
        """Get information about the current branch."""
        try:
            if target_repo == 'ai_repo':
                repo = self._get_ai_repo()
            else:
                repo = self._get_product_repo()
            
            current_branch = repo.active_branch
            
            return {
                "branch_name": current_branch.name,
                "commit_hash": current_branch.commit.hexsha[:8],
                "commit_message": current_branch.commit.message.strip(),
                "is_dirty": repo.is_dirty(untracked_files=True),
                "untracked_files": repo.untracked_files,
                "repo_path": str(repo.working_dir)
            }
        except Exception as e:
            return {"error": str(e)}

    def list_branches(self, target_repo: str = 'product_repo') -> Dict[str, Any]:
        """List all branches in the target repository."""
        try:
            if target_repo == 'ai_repo':
                repo = self._get_ai_repo()
            else:
                repo = self._get_product_repo()
            
            branches = []
            current_branch_name = repo.active_branch.name
            
            for branch in repo.heads:
                branches.append({
                    "name": branch.name,
                    "is_current": branch.name == current_branch_name,
                    "commit_hash": branch.commit.hexsha[:8],
                    "commit_message": branch.commit.message.strip()
                })
            
            return {
                "current_branch": current_branch_name,
                "total_branches": len(branches),
                "branches": branches
            }
        except Exception as e:
            return {"error": str(e)}

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

def commit_and_push_changes(commit_message: str, files: list = None, target_repo: str = 'product_repo') -> str:
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

def create_feature_pull_request(story_id: str, title: str, description: str, target_repo: str = 'product_repo') -> str:
    """Create a pull request for a completed feature."""
    git_tool = create_enhanced_git_tool()
    return git_tool._run('create_pull_request',
                         story_id=story_id,
                         pr_title=title,
                         pr_body=description,
                         target_repo=target_repo)

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
        
        # Test 3: Get branch info
        print("\n3. Getting branch info...")
        git_tool = create_enhanced_git_tool()
        branch_info = git_tool.get_current_branch_info()
        print(f"Current branch: {branch_info}")
        
        print("\n✅ Cross-repository workflow test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Cross-repository workflow test failed: {e}")
        return False

if __name__ == "__main__":
    test_cross_repo_workflow()