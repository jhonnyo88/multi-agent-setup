#!/usr/bin/env python3
"""
GitHub Issue Processing Test Script
==================================

PURPOSE:
Tests the complete workflow from fetching a real GitHub Issue
to processing it through the AI team (Projektledare analysis).

USAGE:
    python scripts/test_github_issue.py --issue-number 1
    python scripts/test_github_issue.py --issue-number 1 --detailed

WHAT THIS SCRIPT DOES:
1. Connects to GitHub API and fetches the specified issue
2. Validates the issue data structure  
3. Passes the issue to Projektledare for analysis
4. Displays the analysis results in a user-friendly format
5. Tests the complete GitHub → AI → Analysis workflow

This helps verify that our AI team can understand and process
real feature requests from the project owner.
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
    from github import Github, Auth
    from agents.projektledare import create_projektledare
    from config.settings import SECRETS, GITHUB_CONFIG
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTo fix this:")
    print("1. Make sure you're in the project root directory")
    print("2. Run: pip install PyGithub")
    print("3. Check that your .env file has ANTHROPIC_API_KEY configured")
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

class GitHubIssueFetcher:
    """Handles fetching GitHub Issues via the API."""
    
    def __init__(self):
        """Initialize GitHub connection."""
        self.github_token = SECRETS.get("github_token")
        if not self.github_token or self.github_token.startswith("[YOUR_"):
            raise ValueError(
                "GitHub token not configured. Please set GITHUB_TOKEN in your .env file.\n"
                "See docs/setup/github_token_setup.md for instructions."
            )
        
        # Initialize GitHub API client
        auth = Auth.Token(self.github_token)
        self.github = Github(auth=auth)
        
        # Repository configuration
        self.repo_owner = GITHUB_CONFIG["ai_team_repo"]["owner"]
        self.repo_name = GITHUB_CONFIG["ai_team_repo"]["name"]
        
        print_success(f"GitHub API connected for {self.repo_owner}/{self.repo_name}")
    
    def fetch_issue(self, issue_number: int) -> dict:
        """
        Fetch a specific GitHub Issue by number.
        
        Args:
            issue_number: The issue number to fetch
            
        Returns:
            Dict containing issue data in our standard format
        """
        try:
            print_info(f"Fetching issue #{issue_number} from GitHub...")
            
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            issue = repo.get_issue(issue_number)
            
            # Convert GitHub Issue to our standard format
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
                "assignees": [{"login": assignee.login} for assignee in issue.assignees],
                "milestone": issue.milestone.title if issue.milestone else None,
                "comments_count": issue.comments
            }
            
            print_success(f"Successfully fetched issue #{issue_number}")
            print_info(f"Title: {issue_data['title']}")
            print_info(f"Author: {issue_data['user']['login']}")
            print_info(f"State: {issue_data['state']}")
            print_info(f"Labels: {', '.join([label['name'] for label in issue_data['labels']])}")
            
            return issue_data
            
        except Exception as e:
            print_error(f"Failed to fetch issue #{issue_number}: {e}")
            print_info("Common issues:")
            print_info("- Issue number doesn't exist")
            print_info("- GitHub token doesn't have 'repo' permission")
            print_info("- Repository name is incorrect")
            print_info("- Network connectivity problems")
            raise

def display_issue_summary(issue_data: dict):
    """Display a summary of the fetched issue."""
    print_section("GitHub Issue Summary")
    
    print(f"📋 Issue #{issue_data['number']}: {issue_data['title']}")
    print(f"👤 Created by: {issue_data['user']['login']}")
    print(f"📅 Created: {issue_data['created_at']}")
    print(f"🏷️  Labels: {', '.join([label['name'] for label in issue_data['labels']])}")
    print(f"📊 State: {issue_data['state']}")
    print(f"💬 Comments: {issue_data['comments_count']}")
    print(f"🔗 URL: {issue_data['url']}")
    
    print(f"\n📝 Issue Body:")
    print("-" * 50)
    # Truncate body for display if it's very long
    body = issue_data['body']
    if len(body) > 1000:
        print(body[:1000] + "\n... (truncated)")
    else:
        print(body)
    print("-" * 50)

async def analyze_issue_with_ai(issue_data: dict, detailed: bool = False) -> dict:
    """
    Process the GitHub Issue through our AI Projektledare.
    
    Args:
        issue_data: The GitHub issue data
        detailed: Whether to show detailed analysis output
        
    Returns:
        Analysis results from the Projektledare
    """
    print_section("AI Team Analysis")
    
    try:
        print_info("Initializing Projektledare agent...")
        projektledare = create_projektledare()
        print_success("Projektledare agent ready")
        
        print_info(f"Analyzing issue #{issue_data['number']} with Claude-3.5-Sonnet...")
        print_info("This may take 30-60 seconds for complex analysis...")
        
        # Run the analysis
        analysis_start = datetime.now()
        analysis_result = await projektledare.analyze_feature_request(issue_data)
        analysis_duration = datetime.now() - analysis_start
        
        print_success(f"Analysis completed in {analysis_duration.total_seconds():.1f} seconds")
        
        return analysis_result
        
    except Exception as e:
        print_error(f"AI analysis failed: {e}")
        print_info("This could be due to:")
        print_info("- ANTHROPIC_API_KEY not configured correctly")
        print_info("- Network issues reaching Anthropic API")
        print_info("- Issue content that's difficult to analyze")
        print_info("- Agent configuration problems")
        raise

def display_analysis_results(analysis: dict, detailed: bool = False):
    """Display the AI analysis results in a user-friendly format."""
    print_section("AI Analysis Results")
    
    # Main recommendation
    recommendation = analysis.get("recommendation", {})
    action = recommendation.get("action", "unknown")
    reasoning = recommendation.get("reasoning", "No reasoning provided")
    
    print(f"🎯 **RECOMMENDATION**: {action.upper()}")
    print(f"💭 **Reasoning**: {reasoning}")
    
    # DNA Alignment
    if "dna_alignment" in analysis:
        print_info("\n📋 DNA Alignment Check:")
        dna = analysis["dna_alignment"]
        print(f"   Vision/Mission Aligned: {'✅' if dna.get('vision_mission_aligned') else '❌'}")
        print(f"   Target Audience Served: {'✅' if dna.get('target_audience_served') else '❌'}")
        print(f"   Design Principles Compatible: {'✅' if dna.get('design_principles_compatible') else '❌'}")
        
        if dna.get("concerns"):
            print_warning("   Concerns identified:")
            for concern in dna["concerns"]:
                print(f"     - {concern}")
    
    # Complexity Assessment
    if "complexity" in analysis:
        print_info("\n📊 Complexity Assessment:")
        complexity = analysis["complexity"]
        print(f"   Estimated Stories: {complexity.get('estimated_stories', 'unknown')}")
        print(f"   Estimated Days: {complexity.get('estimated_days', 'unknown')}")
        print(f"   Complexity Level: {complexity.get('complexity_level', 'unknown')}")
        print(f"   Required Agents: {', '.join(complexity.get('required_agents', []))}")
    
    # Technical Feasibility
    if "technical_feasibility" in analysis:
        print_info("\n🔧 Technical Feasibility:")
        tech = analysis["technical_feasibility"]
        print(f"   Architecture Compatible: {'✅' if tech.get('architecture_compatible') else '❌'}")
        print(f"   Deployment Feasible: {'✅' if tech.get('deployment_feasible') else '❌'}")
        
        if tech.get("technical_risks"):
            print_warning("   Technical Risks:")
            for risk in tech["technical_risks"]:
                print(f"     - {risk}")
    
    # Next Steps
    if "next_steps" in recommendation:
        print_info("\n🚀 Recommended Next Steps:")
        for step in recommendation["next_steps"]:
            print(f"   - {step}")
    
    # Show full JSON if detailed mode
    if detailed:
        print_section("Complete Analysis Data (JSON)")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

async def test_story_breakdown(projektledare, analysis: dict, issue_data: dict):
    """Test the story breakdown functionality if the feature was approved."""
    if analysis.get("recommendation", {}).get("action") != "approve":
        print_info("Skipping story breakdown - feature was not approved")
        return None
    
    print_section("Story Breakdown Test")
    
    try:
        print_info("Creating story breakdown...")
        stories = await projektledare.create_story_breakdown(analysis, issue_data)
        
        if stories and len(stories) > 0:
            print_success(f"Created {len(stories)} implementation stories")
            
            for i, story in enumerate(stories, 1):
                print(f"\n📋 Story {i}: {story.get('story_id', 'NO-ID')}")
                print(f"   Title: {story.get('title', 'No title')}")
                print(f"   Assigned Agent: {story.get('assigned_agent', 'unknown')}")
                print(f"   Story Type: {story.get('story_type', 'unknown')}")
                print(f"   Estimated Effort: {story.get('estimated_effort', 'unknown')}")
                print(f"   Acceptance Criteria: {len(story.get('acceptance_criteria', []))} items")
                
                # Show first acceptance criterion as example
                criteria = story.get('acceptance_criteria', [])
                if criteria:
                    print(f"   Example Criterion: {criteria[0]}")
        
        return stories
        
    except Exception as e:
        print_error(f"Story breakdown failed: {e}")
        return None

def save_results_to_file(issue_data: dict, analysis: dict, stories: list = None):
    """Save the test results to a file for later reference."""
    results = {
        "test_timestamp": datetime.now().isoformat(),
        "github_issue": issue_data,
        "ai_analysis": analysis,
        "story_breakdown": stories,
        "ai_model": "claude-3.5-sonnet",
        "test_version": "1.0"
    }
    
    # Save to reports directory
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    filename = f"issue_{issue_data['number']}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = reports_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print_success(f"Results saved to {filepath}")
        print_info("You can review this file to see the complete analysis")
        
    except Exception as e:
        print_warning(f"Could not save results: {e}")

async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test GitHub Issue processing with AI team")
    parser.add_argument("--issue-number", "-i", type=int, required=True, 
                       help="GitHub issue number to process")
    parser.add_argument("--detailed", "-d", action="store_true",
                       help="Show detailed analysis output including full JSON")
    parser.add_argument("--skip-stories", action="store_true",
                       help="Skip story breakdown test (faster)")
    
    args = parser.parse_args()
    
    print("🤖 DigiNativa AI-Team - GitHub Issue Processing Test")
    print("=" * 70)
    print(f"Testing with Issue #{args.issue_number}")
    print(f"Detailed output: {args.detailed}")
    print(f"Story breakdown: {not args.skip_stories}")
    
    try:
        # Step 1: Fetch the GitHub Issue
        print_section("Step 1: Fetching GitHub Issue")
        fetcher = GitHubIssueFetcher()
        issue_data = fetcher.fetch_issue(args.issue_number)
        display_issue_summary(issue_data)
        
        # Step 2: Analyze with AI
        print_section("Step 2: AI Analysis")
        analysis = await analyze_issue_with_ai(issue_data, args.detailed)
        display_analysis_results(analysis, args.detailed)
        
        # Step 3: Test Story Breakdown (if approved and not skipped)
        stories = None
        if not args.skip_stories:
            projektledare = create_projektledare()  # Reuse the agent
            stories = await test_story_breakdown(projektledare, analysis, issue_data)
        
        # Step 4: Save Results
        print_section("Step 4: Saving Results")
        save_results_to_file(issue_data, analysis, stories)
        
        # Summary
        print_section("Test Summary")
        recommendation = analysis.get("recommendation", {}).get("action", "unknown")
        print_success("✅ GitHub Issue processing test completed successfully!")
        print_info(f"Issue #{args.issue_number} analysis result: {recommendation.upper()}")
        
        if stories:
            print_info(f"Generated {len(stories)} implementation stories")
        
        print_info("Next steps:")
        if recommendation == "approve":
            print_info("- The AI team is ready to implement this feature")
            print_info("- You can now run the full development workflow")
            print_info("- Consider creating the actual GitHub issues for each story")
        elif recommendation == "clarify":
            print_info("- The feature request needs clarification")
            print_info("- Review the analysis reasoning for specific questions")
            print_info("- Update the GitHub issue with more details")
        else:
            print_info(f"- Review the {recommendation} recommendation")
            print_info("- Consider if the feature aligns with project goals")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        print_info("\nTroubleshooting:")
        print_info("1. Check your .env file has correct API keys")
        print_info("2. Verify the issue number exists")
        print_info("3. Ensure network connectivity")
        print_info("4. Run: python scripts/setup.py to verify configuration")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)