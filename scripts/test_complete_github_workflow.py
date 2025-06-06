#!/usr/bin/env python3
"""
Complete GitHub Workflow Test Script
==================================

PURPOSE:
Tests the complete AI team workflow including:
1. Fetching GitHub Issue
2. AI Projektledare analysis  
3. Posting analysis results to GitHub
4. Creating story breakdown issues (if approved)

This verifies the full integration between AI team and GitHub.

USAGE:
    python scripts/test_complete_github_workflow.py --issue-number 1
    python scripts/test_complete_github_workflow.py --issue-number 1 --dry-run

WHAT THIS SCRIPT DOES:
1. Fetches the specified GitHub Issue
2. Runs it through Projektledare analysis
3. Posts the analysis as a comment on GitHub
4. Creates story breakdown issues if feature is approved
5. Saves complete results to reports directory
6. Provides detailed feedback on what happened

This is the ultimate test of our AI team's GitHub integration.
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from agents.projektledare import process_github_issue_complete_workflow
    from workflows.github_integration.project_owner_communication import ProjectOwnerCommunication
    from config.settings import GITHUB_CONFIG
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTo fix this:")
    print("1. Make sure you're in the project root directory")
    print("2. Check that your .env file has GITHUB_TOKEN and ANTHROPIC_API_KEY configured")
    print("3. Run: pip install PyGithub")
    sys.exit(1)

def print_section(title: str):
    """Print a clear section header."""
    print(f"\n{'='*70}")
    print(f"🔍 {title}")
    print(f"{'='*70}")

def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")

def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")

def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message.""" 
    print(f"⚠️  {message}")

def display_workflow_results(results: dict, issue_number: int):
    """Display the complete workflow results in a user-friendly format."""
    print_section("Complete Workflow Results")
    
    # Overall status
    if "error" in results:
        print_error(f"Workflow failed: {results['error']}")
        return
    
    # Analysis results
    analysis = results.get("analysis", {})
    recommendation = analysis.get("recommendation", {})
    action = recommendation.get("action", "unknown").upper()
    
    print(f"🎯 **OVERALL RESULT**: {action}")
    print(f"💭 **AI Reasoning**: {recommendation.get('reasoning', 'No reasoning provided')}")
    print(f"⏱️  **Workflow Duration**: {results.get('workflow_duration_seconds', 0):.1f} seconds")
    
    # GitHub integration results
    print_info("\n🐙 GitHub Integration Results:")
    github_updated = results.get("github_updated", False)
    print(f"   Analysis posted to GitHub: {'✅ YES' if github_updated else '❌ NO'}")
    
    stories_created = results.get("stories_created", 0)
    print(f"   Story issues created: {stories_created}")
    
    if stories_created > 0:
        print_info("   📋 Created Story Issues:")
        for story_issue in results.get("story_issues", []):
            print(f"     - #{story_issue['number']}: {story_issue['story_id']} (→ {story_issue['assigned_agent']})")
            print(f"       URL: {story_issue['url']}")
    
    # DNA Alignment
    if "dna_alignment" in analysis:
        print_info("\n📋 DNA Alignment Check:")
        dna = analysis["dna_alignment"]
        print(f"   Vision/Mission Aligned: {'✅' if dna.get('vision_mission_aligned') else '❌'}")
        print(f"   Target Audience Served: {'✅' if dna.get('target_audience_served') else '❌'}")
        print(f"   Design Principles Compatible: {'✅' if dna.get('design_principles_compatible') else '❌'}")
    
    # Complexity Assessment
    if "complexity" in analysis:
        print_info("\n📊 Complexity Assessment:")
        complexity = analysis["complexity"]
        print(f"   Estimated Stories: {complexity.get('estimated_stories', 'unknown')}")
        print(f"   Estimated Days: {complexity.get('estimated_days', 'unknown')}")
        print(f"   Required Agents: {', '.join(complexity.get('required_agents', []))}")
    
    # What happened on GitHub
    print_info(f"\n🔗 GitHub Activity:")
    repo_config = GITHUB_CONFIG['ai_team_repo']
    issue_url = f"https://github.com/{repo_config['owner']}/{repo_config['name']}/issues/{issue_number}"
    print(f"   Check the GitHub issue: {issue_url}")
    
    if github_updated:
        print_info("   You should see a new AI analysis comment on the issue")
    
    if stories_created > 0:
        project_repo_config = GITHUB_CONFIG['project_repo']
        project_url = f"https://github.com/{project_repo_config['owner']}/{project_repo_config['name']}/issues"
        print_info(f"   Check the project repo for new story issues: {project_url}")

def save_workflow_results(results: dict, issue_number: int):
    """Save the complete workflow results to a file."""
    try:
        # Create reports directory if it doesn't exist
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"complete_workflow_issue_{issue_number}_{timestamp}.json"
        filepath = reports_dir / filename
        
        # Add metadata to results
        results_with_meta = {
            "test_metadata": {
                "test_type": "complete_github_workflow",
                "issue_number": issue_number,
                "test_timestamp": datetime.now().isoformat(),
                "ai_model": "claude-3-5-sonnet",
                "test_version": "1.0"
            },
            "workflow_results": results
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_with_meta, f, indent=2, ensure_ascii=False)
        
        print_success(f"Workflow results saved to {filepath}")
        print_info("This file contains the complete audit trail of the AI team's work")
        
    except Exception as e:
        print_warning(f"Could not save workflow results: {e}")

async def run_dry_run_test(issue_number: int):
    """
    Run a dry-run test that fetches and analyzes but doesn't post to GitHub.
    """
    print_section("Dry-Run Mode (No GitHub Updates)")
    print_info("This will analyze the issue but NOT post comments or create issues")
    
    try:
        # Initialize GitHub communication for fetching only
        github_comm = ProjectOwnerCommunication()
        
        # Fetch the issue
        print_info(f"Fetching issue #{issue_number}...")
        repo = github_comm.github.ai_repo
        issue = repo.get_issue(issue_number)
        
        # Convert to standard format
        issue_data = {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "labels": [{"name": label.name} for label in issue.labels],
            "user": {"login": issue.user.login},
            "state": issue.state,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "url": issue.html_url
        }
        
        print_success(f"Fetched issue: {issue_data['title']}")
        
        # Run AI analysis only (no GitHub updates)
        from agents.projektledare import create_projektledare
        
        print_info("Running AI analysis...")
        projektledare = create_projektledare()
        analysis = await projektledare.analyze_feature_request(issue_data)
        
        # Show what would have been posted to GitHub
        print_section("Analysis Results (Would be posted to GitHub)")
        
        recommendation = analysis.get("recommendation", {})
        action = recommendation.get("action", "unknown")
        
        print(f"🎯 AI Recommendation: {action.upper()}")
        print(f"💭 Reasoning: {recommendation.get('reasoning', 'No reasoning provided')}")
        
        if action == "approve":
            print_info("✅ Feature would be APPROVED")
            print_info("📋 Story breakdown would be created")
            print_info("📝 GitHub issues would be created for each story")
        elif action == "clarify":
            print_warning("❓ Feature needs CLARIFICATION")
            print_info("💬 GitHub comment would ask for more details")
        elif action == "reject":
            print_error("❌ Feature would be REJECTED")
            print_info("💬 GitHub comment would explain why")
        
        # Simulate what the GitHub comment would look like
        print_section("Simulated GitHub Comment Preview")
        print("📝 This is what would be posted to GitHub:")
        print("-" * 50)
        
        # Use the same formatting as the real GitHub integration
        comment_preview = github_comm.github._format_analysis_comment(analysis, issue_data)
        # Show first 500 characters
        print(comment_preview[:500] + "..." if len(comment_preview) > 500 else comment_preview)
        print("-" * 50)
        
        dry_run_results = {
            "dry_run": True,
            "analysis": analysis,
            "issue_data": issue_data,
            "would_post_to_github": True,
            "comment_preview": comment_preview[:200] + "..." if len(comment_preview) > 200 else comment_preview
        }
        
        return dry_run_results
        
    except Exception as e:
        print_error(f"Dry-run test failed: {e}")
        return {"dry_run": True, "error": str(e)}

async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test complete GitHub workflow with AI team")
    parser.add_argument("--issue-number", "-i", type=int, required=True, 
                       help="GitHub issue number to process")
    parser.add_argument("--dry-run", "-d", action="store_true",
                       help="Analyze only, don't post to GitHub (safe for testing)")
    
    args = parser.parse_args()
    
    print("🤖 DigiNativa AI-Team - Complete GitHub Workflow Test")
    print("=" * 70)
    print(f"Testing with Issue #{args.issue_number}")
    
    if args.dry_run:
        print("🔒 DRY-RUN MODE: Will analyze but not post to GitHub")
    else:
        print("🚀 LIVE MODE: Will post analysis and create issues on GitHub")
        print("⚠️  This will make real changes to GitHub repositories!")
        
        # Confirmation for live mode
        confirm = input("\nAre you sure you want to proceed with live GitHub updates? (yes/no): ")
        if confirm.lower() != "yes":
            print("Test cancelled by user")
            return False
    
    try:
        if args.dry_run:
            # Run dry-run mode
            results = await run_dry_run_test(args.issue_number)
        else:
            # Run complete workflow with GitHub updates
            print_section("Running Complete GitHub Workflow")
            results = await process_github_issue_complete_workflow(args.issue_number)
        
        # Display results
        if args.dry_run:
            print_section("Dry-Run Results Summary")
            if "error" not in results:
                print_success("✅ Dry-run completed successfully!")
                analysis = results.get("analysis", {})
                action = analysis.get("recommendation", {}).get("action", "unknown")
                print_info(f"AI would recommend: {action.upper()}")
            else:
                print_error(f"Dry-run failed: {results['error']}")
        else:
            display_workflow_results(results, args.issue_number)
            
            # Save results
            save_workflow_results(results, args.issue_number)
        
        # Final summary
        print_section("Test Summary")
        
        if "error" not in results:
            if args.dry_run:
                print_success("✅ Dry-run test completed successfully!")
                print_info("The AI team analyzed the issue without making GitHub changes")
                print_info("Run without --dry-run to execute the full workflow")
            else:
                print_success("✅ Complete GitHub workflow test completed successfully!")
                github_updated = results.get("github_updated", False)
                stories_created = results.get("stories_created", 0)
                
                if github_updated:
                    print_info("🐙 GitHub was updated with AI analysis")
                if stories_created > 0:
                    print_info(f"📋 {stories_created} story issues were created")
                
                print_info("Check GitHub to see the AI team's work!")
        else:
            print_error("❌ Test failed - check error messages above")
            
        return "error" not in results
        
    except Exception as e:
        print_error(f"Test failed with unexpected error: {e}")
        print_info("\nTroubleshooting:")
        print_info("1. Check your .env file has correct API keys")
        print_info("2. Verify the issue number exists")
        print_info("3. Ensure GitHub token has correct permissions")
        print_info("4. Check network connectivity")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)