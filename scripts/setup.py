#!/usr/bin/env python3
"""
DigiNativa AI-Team Setup Script
==============================

PURPOSE:
Interactive setup wizard that helps users configure the DigiNativa AI-Team
for their environment. This script validates dependencies, creates necessary
files, and tests connections to external services.

ADAPTATION GUIDE:
🔧 To adapt this setup script for your project:
1. Line 45-50: Update required environment variables for your domain
2. Line 80-95: Modify dependency checks for your tech stack
3. Line 120-140: Adapt database initialization for your data needs
4. Line 160-180: Update service connection tests for your integrations

WHAT THIS SCRIPT DOES:
1. Validates Python version and project structure
2. Creates .env file from template if it doesn't exist
3. Checks that all required API keys are configured
4. Initializes SQLite database for agent state management
5. Tests connections to GitHub and OpenAI APIs
6. Provides next steps for the user

DEPENDENCIES:
- Python 3.9+
- .env.template file must exist in project root
- Internet connection for API testing
"""

import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv
import subprocess

def print_header():
    """Print welcome message and setup information"""
    print("🚀 DigiNativa AI-Team Setup Wizard")
    print("=" * 50)
    print("This script will help you configure your AI team environment.")
    print("Make sure you have your API keys ready!\n")

def check_python_version():
    """
    Validate that Python version is 3.9 or higher.
    
    WHY THIS MATTERS:
    The CrewAI framework and modern type hints require Python 3.9+.
    Older versions will cause import errors and type annotation issues.
    """
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9+ required for CrewAI compatibility")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again.")
        sys.exit(1)
    
    print(f"✅ Python version OK: {sys.version.split()[0]}")

def check_project_structure():
    """
    Verify we're running from the correct project directory.
    
    WHAT WE'RE CHECKING:
    - .env.template exists (needed to create .env)
    - config/ directory exists (our configuration files)
    - docs/ directory exists (project DNA documents)
    
    This prevents running the script from wrong location.
    """
    required_files = [".env.template", "config", "docs"]
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Error: Missing required project files/directories:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("   Please run this script from the project root directory.")
        sys.exit(1)
    
    print("✅ Project structure detected")

def setup_environment_file():
    """
    Create .env file from template if it doesn't exist.
    
    SECURITY NOTE:
    The .env file will contain your API keys and should NEVER be committed
    to git. It's already included in .gitignore for protection.
    
    🔧 ADAPTATION: Add any additional environment variables your project needs
    """
    env_file = Path(".env")
    template_file = Path(".env.template")
    
    if not env_file.exists():
        print("\n📝 Creating .env file from template...")
        shutil.copy(template_file, env_file)
        print("✅ .env file created")
        print("🔧 IMPORTANT: Please edit .env with your API keys before continuing")
        print("   Required keys: OPENAI_API_KEY, GITHUB_TOKEN")
        print("   Optional: NETLIFY_TOKEN, WEBHOOK_SECRET")
        
        # Give user chance to configure .env
        response = input("\nHave you configured your .env file with API keys? (y/n): ")
        if response.lower() != 'y':
            print("Please configure .env and run setup again")
            print("Tip: You can edit .env in VS Code while this script waits")
            sys.exit(0)
    else:
        print("✅ .env file already exists")

def validate_environment_variables():
    """
    Check that all required environment variables are configured.
    
    REQUIRED VARIABLES:
    - OPENAI_API_KEY: For AI agent LLM calls
    - GITHUB_TOKEN: For GitHub Issues API and repository automation
    
    OPTIONAL VARIABLES:
    - NETLIFY_TOKEN: For automated deployment (can be added later)
    - WEBHOOK_SECRET: For GitHub webhook security (can be generated later)
    
    🔧 ADAPTATION: Update required_vars list for your integrations
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Define which variables are absolutely required
    required_vars = ["OPENAI_API_KEY", "GITHUB_TOKEN"]  # 🔧 ADD YOUR REQUIRED VARS HERE
    optional_vars = ["NETLIFY_TOKEN", "WEBHOOK_SECRET"]  # 🔧 ADD YOUR OPTIONAL VARS HERE
    
    missing_vars = []
    unconfigured_vars = []
    
    # Check each required variable
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value.startswith("[YOUR_"):
            unconfigured_vars.append(var)
    
    # Report any problems
    if missing_vars or unconfigured_vars:
        print("❌ Environment configuration issues:")
        if missing_vars:
            print(f"   Missing variables: {', '.join(missing_vars)}")
        if unconfigured_vars:
            print(f"   Unconfigured placeholders: {', '.join(unconfigured_vars)}")
        print("   Please configure these in your .env file")
        sys.exit(1)
    
    # Check optional variables (warn but don't fail)
    for var in optional_vars:
        value = os.getenv(var)
        if not value or value.startswith("[YOUR_"):
            print(f"⚠️  Optional variable {var} not configured (can be added later)")
    
    print("✅ Required environment variables configured")

def initialize_state_directory():
    """
    Create and initialize the state directory for agent data storage.
    
    WHAT THIS CREATES:
    - state/ directory: For SQLite database and agent memory
    - state/logs/ directory: For agent execution logs
    - state/backups/ directory: For database backups
    
    WHY THIS MATTERS:
    Agents need persistent storage to remember conversation history,
    track story progress, and maintain state across restarts.
    """
    state_dir = Path("state")
    logs_dir = state_dir / "logs"
    backups_dir = state_dir / "backups"
    
    # Create directories if they don't exist
    state_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    backups_dir.mkdir(exist_ok=True)
    
    # Create initial database schema (will be implemented later)
    print("\n💾 Initializing state management...")
    
    # TODO: When we implement state/database.py, call init_database() here
    # try:
    #     from state.database import init_database
    #     init_database()
    #     print("✅ Database schema initialized")
    # except ImportError:
    #     print("ℹ️  Database initialization deferred (will be done when agents start)")
    
    print("✅ State directories created")

def test_github_connection():
    """
    Test connection to GitHub API using the provided token.
    
    WHAT THIS TESTS:
    1. GitHub token has correct format
    2. Token has required permissions (repo access)
    3. Can successfully make API calls
    
    REQUIRED PERMISSIONS:
    - repo: Full repository access for creating issues, PRs
    - read:org: To read organization information
    - write:discussion: For GitHub Discussions (optional)
    
    🔧 ADAPTATION: Add tests for other APIs your project uses
    """
    print("\n🔗 Testing GitHub connection...")
    
    try:
        import requests
        
        # Get token from environment
        token = os.getenv('GITHUB_TOKEN')
        headers = {"Authorization": f"token {token}"}
        
        # Test basic API access
        response = requests.get("https://api.github.com/user", headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Connected to GitHub as: {user['login']}")
            
            # Test repository access
            repo_owner = os.getenv('AI_TEAM_REPO_OWNER', 'jhonnyo88')
            repo_name = os.getenv('AI_TEAM_REPO_NAME', 'multi-agent-setup')
            repo_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
            
            repo_response = requests.get(repo_url, headers=headers)
            if repo_response.status_code == 200:
                print(f"✅ Repository access confirmed: {repo_owner}/{repo_name}")
            else:
                print(f"⚠️  Cannot access repository {repo_owner}/{repo_name}")
                print("   Check repository exists and token has repo permissions")
        
        elif response.status_code == 401:
            print("❌ GitHub authentication failed")
            print("   Check your GITHUB_TOKEN is correct and not expired")
            sys.exit(1)
        else:
            print(f"❌ GitHub API error: {response.status_code}")
            print("   Check your internet connection and GitHub token")
            sys.exit(1)
            
    except ImportError:
        print("❌ 'requests' library not installed")
        print("   Run: pip install requests")
        sys.exit(1)
    except Exception as e:
        print(f"❌ GitHub connection test failed: {e}")
        sys.exit(1)

def test_openai_connection():
    """
    Test connection to OpenAI API using the provided key.
    
    WHAT THIS TESTS:
    1. OpenAI API key is valid and not expired
    2. Can make successful API calls
    3. Has access to required models (GPT-4)
    
    WHY THIS MATTERS:
    All AI agents depend on OpenAI for language model capabilities.
    Invalid keys will cause all agent operations to fail.
    
    🔧 ADAPTATION: Add tests for other AI providers (Anthropic, etc.)
    """
    print("\n🤖 Testing OpenAI connection...")
    
    try:
        import openai
        
        # Configure OpenAI client
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test API access by listing available models
        models = client.models.list()
        print("✅ OpenAI connection successful")
        
        # Check if GPT-4 is available (required for best agent performance)
        model_names = [model.id for model in models.data]
        if any("gpt-4" in model for model in model_names):
            print("✅ GPT-4 access confirmed")
        else:
            print("⚠️  GPT-4 not available, will use GPT-3.5-turbo")
            
    except openai.AuthenticationError:
        print("❌ OpenAI authentication failed")
        print("   Check your OPENAI_API_KEY is correct")
        sys.exit(1)
    except Exception as e:
        print(f"❌ OpenAI connection test failed: {e}")
        print("   Check your OPENAI_API_KEY in .env file")
        sys.exit(1)

def print_next_steps():
    """
    Display next steps for the user after successful setup.
    
    This guides the user through the remaining setup tasks that
    can't be automated (like customizing DNA documents).
    """
    print("\n🎉 Setup complete! Your DigiNativa AI-Team is ready.")
    print("\n📋 Next steps:")
    print("1. 📚 Review and customize docs/dna/ files for your project:")
    print("   - vision_and_mission.md: Define your project goals")
    print("   - target_audience.md: Describe your users (like 'Anna')")
    print("   - design_principles.md: Set your 5 core design principles")
    print("   - architecture.md: Confirm tech stack choices")
    
    print("\n2. 🚀 Start your AI team:")
    print("   python scripts/deploy_agents.py")
    
    print("\n3. 📝 Create your first feature request:")
    print("   - Go to GitHub Issues in your repository")
    print("   - Click 'New Issue' and use the Feature Request template")
    print("   - Fill in details about what you want to build")
    
    print("\n4. 📊 Monitor your team:")
    print("   python scripts/health_check.py  # Check system status")
    print("   python -m pytest tests/         # Run tests")
    
    print("\n🔧 Configuration files created:")
    print("   - .env (your API keys - keep this secret!)")
    print("   - state/ (agent memory and logs)")
    print("   - All project files ready for customization")
    
    print("\n📖 Need help? Check the documentation:")
    print("   - README.md: Project overview")
    print("   - docs/implementation/: Technical guides")
    print("   - PROJECT_SUMMARY.md: Complete project context")

def main():
    """
    Main setup function that orchestrates all setup steps.
    
    SETUP FLOW:
    1. Welcome and system checks
    2. Environment configuration
    3. Service connection testing
    4. Guidance for next steps
    
    ERROR HANDLING:
    Script will exit with helpful error messages if any step fails.
    This prevents incomplete setups that would cause agent failures.
    """
    try:
        # Step 1: Basic validation
        print_header()
        check_python_version()
        check_project_structure()
        
        # Step 2: Environment setup
        setup_environment_file()
        validate_environment_variables()
        
        # Step 3: Initialize project structure
        initialize_state_directory()
        
        # Step 4: Test external service connections
        test_github_connection()
        test_openai_connection()
        
        # Step 5: Success and next steps
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        print("Please check the error above and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()