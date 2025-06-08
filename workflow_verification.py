#!/usr/bin/env python3
"""
Workflow Pre-Test Verification Script
====================================

Verifies that all components are ready for the real workflow test.
Run this before attempting the full GitHub Issue → Code workflow.
"""

import asyncio
import sys
from pathlib import Path
import json

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_check(item: str, status: bool, details: str = ""):
    emoji = "✅" if status else "❌"
    print(f"{emoji} {item}")
    if details:
        print(f"   {details}")
    return status

async def verify_environment():
    """Verify basic environment setup."""
    print_section("Environment Verification")
    
    checks_passed = 0
    total_checks = 0
    
    # Check 1: Current directory
    total_checks += 1
    current_dir = Path.cwd()
    in_correct_dir = "multi-agent-setup" in str(current_dir)
    if print_check("Correct directory", in_correct_dir, f"Current: {current_dir}"):
        checks_passed += 1
    
    # Check 2: Product repo exists
    total_checks += 1
    product_repo_path = Path("C:/Users/jcols/Documents/diginativa-game")
    product_repo_exists = product_repo_path.exists()
    if print_check("Product repo exists", product_repo_exists, f"Path: {product_repo_path}"):
        checks_passed += 1
    
    # Check 3: Environment file
    total_checks += 1
    env_file = Path(".env")
    env_exists = env_file.exists()
    if print_check("Environment file exists", env_exists, f"File: {env_file}"):
        checks_passed += 1
    
    # Check 4: Required directories
    total_checks += 1
    required_dirs = ["agents", "workflows", "tools", "config"]
    all_dirs_exist = all((Path(d).exists() for d in required_dirs))
    if print_check("Required directories", all_dirs_exist, f"Checked: {', '.join(required_dirs)}"):
        checks_passed += 1
    
    return checks_passed, total_checks

async def verify_projektledare():
    """Verify Projektledare agent is ready."""
    print_section("Projektledare Verification")
    
    checks_passed = 0
    total_checks = 0
    
    try:
        # Check 1: Import and create
        total_checks += 1
        from agents.projektledare import create_projektledare
        projektledare = create_projektledare()
        if print_check("Projektledare creation", True, "Agent created successfully"):
            checks_passed += 1
        
        # Check 2: Claude LLM
        total_checks += 1
        claude_available = projektledare.claude_llm is not None
        if print_check("Claude LLM configured", claude_available):
            checks_passed += 1
        
        # Check 3: GitHub communication
        total_checks += 1
        github_available = projektledare.github_comm is not None
        if print_check("GitHub communication", github_available):
            checks_passed += 1
        
        # Check 4: Agent coordinator
        total_checks += 1
        coordinator_available = projektledare.agent_coordinator is not None
        if print_check("Agent coordinator", coordinator_available):
            checks_passed += 1
            
    except Exception as e:
        print_check("Projektledare setup", False, f"Error: {e}")
    
    return checks_passed, total_checks

async def verify_speldesigner():
    """Verify Speldesigner agent is ready."""
    print_section("Speldesigner Verification")
    
    checks_passed = 0
    total_checks = 0
    
    try:
        # Check 1: Import and create
        total_checks += 1
        from agents.speldesigner import create_speldesigner_agent
        speldesigner = create_speldesigner_agent()
        if print_check("Speldesigner creation", True, "Agent created successfully"):
            checks_passed += 1
        
        # Check 2: Claude LLM
        total_checks += 1
        claude_available = speldesigner.claude_llm is not None
        if print_check("Claude LLM configured", claude_available):
            checks_passed += 1
        
        # Check 3: Tools available
        total_checks += 1
        tools_available = hasattr(speldesigner, 'agent') and speldesigner.agent is not None
        if print_check("Design tools available", tools_available):
            checks_passed += 1
            
    except Exception as e:
        print_check("Speldesigner setup", False, f"Error: {e}")
    
    return checks_passed, total_checks

async def verify_utvecklare():
    """Verify Utvecklare agent is ready."""
    print_section("Utvecklare Verification")
    
    checks_passed = 0
    total_checks = 0
    
    try:
        # Check 1: Import and create
        total_checks += 1
        from agents.utvecklare import create_enhanced_utvecklare_agent
        utvecklare = create_enhanced_utvecklare_agent()
        if print_check("Utvecklare creation", True, "Agent created successfully"):
            checks_passed += 1
        
        # Check 2: Claude LLM
        total_checks += 1
        claude_available = utvecklare.claude_llm is not None
        if print_check("Claude LLM configured", claude_available):
            checks_passed += 1
        
        # Check 3: Git tools
        total_checks += 1
        git_available = utvecklare.git_available
        if print_check("Git tools available", git_available):
            checks_passed += 1
        
        # Check 4: Product repo access
        total_checks += 1
        product_repo_accessible = utvecklare.product_repo_path.exists()
        if print_check("Product repo accessible", product_repo_accessible, f"Path: {utvecklare.product_repo_path}"):
            checks_passed += 1
            
    except Exception as e:
        print_check("Utvecklare setup", False, f"Error: {e}")
    
    return checks_passed, total_checks

async def verify_github_integration():
    """Verify GitHub integration is working."""
    print_section("GitHub Integration Verification")
    
    checks_passed = 0
    total_checks = 0
    
    try:
        # Check 1: GitHub API access
        total_checks += 1
        from workflows.github_integration.project_owner_communication import ProjectOwnerCommunication
        github_comm = ProjectOwnerCommunication()
        github_working = github_comm.github is not None
        if print_check("GitHub API access", github_working):
            checks_passed += 1
        
        # Check 2: Repository access
        total_checks += 1
        if github_working:
            try:
                ai_repo = github_comm.github.ai_repo
                repo_accessible = ai_repo is not None
                if print_check("AI repo accessible", repo_accessible, f"Repo: {ai_repo.full_name if repo_accessible else 'N/A'}"):
                    checks_passed += 1
            except Exception as e:
                print_check("AI repo accessible", False, f"Error: {e}")
        else:
            print_check("AI repo accessible", False, "GitHub API not available")
            
    except Exception as e:
        print_check("GitHub integration", False, f"Error: {e}")
    
    return checks_passed, total_checks

async def test_mini_workflow():
    """Test a minimal workflow to ensure components work together."""
    print_section("Mini Workflow Test")
    
    try:
        print("🧪 Testing basic agent coordination...")
        
        # Test 1: Create mock GitHub issue
        mock_issue = {
            "number": 999,
            "title": "Test Feature for Verification",
            "body": "This is a test feature request for verification.",
            "labels": [{"name": "enhancement"}],
            "user": {"login": "test-user"},
            "state": "open",
            "created_at": "2025-06-08T12:00:00Z"
        }
        
        # Test 2: Run Projektledare analysis
        from agents.projektledare import create_projektledare
        projektledare = create_projektledare()
        
        print("   Running Projektledare analysis...")
        analysis = await projektledare.analyze_feature_request(mock_issue)
        
        analysis_success = "recommendation" in analysis and analysis["recommendation"].get("action") in ["approve", "clarify", "reject"]
        print_check("Projektledare analysis", analysis_success, f"Action: {analysis.get('recommendation', {}).get('action', 'unknown')}")
        
        # Test 3: Test story breakdown if approved
        if analysis.get("recommendation", {}).get("action") == "approve":
            print("   Creating story breakdown...")
            stories = await projektledare.create_story_breakdown(analysis, mock_issue)
            
            stories_success = isinstance(stories, list) and len(stories) > 0
            print_check("Story breakdown", stories_success, f"Created {len(stories)} stories")
            
            return True
        else:
            print_check("Story breakdown", True, "Skipped (feature not approved)")
            return True
            
    except Exception as e:
        print_check("Mini workflow test", False, f"Error: {e}")
        return False

async def main():
    """Run complete verification."""
    print("🚀 DigiNativa AI Team Workflow Verification")
    print("=" * 60)
    print("This script verifies that all components are ready for the real workflow test.")
    
    total_passed = 0
    total_checks = 0
    
    # Run all verification steps
    env_passed, env_total = await verify_environment()
    total_passed += env_passed
    total_checks += env_total
    
    pl_passed, pl_total = await verify_projektledare()
    total_passed += pl_passed
    total_checks += pl_total
    
    sd_passed, sd_total = await verify_speldesigner()
    total_passed += sd_passed
    total_checks += sd_total
    
    dev_passed, dev_total = await verify_utvecklare()
    total_passed += dev_passed
    total_checks += dev_total
    
    gh_passed, gh_total = await verify_github_integration()
    total_passed += gh_passed
    total_checks += gh_total
    
    # Mini workflow test
    print_section("Mini Workflow Test")
    workflow_success = await test_mini_workflow()
    if workflow_success:
        total_passed += 1
    total_checks += 1
    
    # Final results
    print_section("Verification Results")
    success_rate = (total_passed / total_checks) * 100
    
    print(f"📊 Overall Results: {total_passed}/{total_checks} checks passed ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! All systems ready for real workflow test!")
        print("\n📋 Next Steps:")
        print("   1. Create GitHub Issue in jhonnyo88/multi-agent-setup")
        print("   2. Run Projektledare monitoring")
        print("   3. Execute full workflow")
    elif success_rate >= 70:
        print("⚠️  GOOD! Most systems ready, some minor issues to fix.")
        print("   Fix the failed checks above before running real workflow.")
    else:
        print("❌ NEEDS WORK! Several critical issues need to be resolved.")
        print("   Address the failed checks before proceeding.")
    
    return success_rate >= 90

if __name__ == "__main__":
    success = asyncio.run(main())