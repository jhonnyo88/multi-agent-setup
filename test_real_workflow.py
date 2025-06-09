#!/usr/bin/env python3
"""
Real Workflow Test - GitHub Issue to Production Code
==================================================

Tests the complete AI team workflow with a real GitHub issue.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"🚀 {title}")
    print(f"{'='*70}")

def print_step(step: str):
    print(f"\n🔹 {step}")

def print_success(message: str):
    print(f"✅ {message}")

def print_info(message: str):
    print(f"ℹ️  {message}")

def print_error(message: str):
    print(f"❌ {message}")

async def test_real_workflow():
    """Test complete workflow from GitHub Issue to Production Code."""
    
    print_section("Real AI Team Workflow Test")
    print("Testing: GitHub Issue → Analysis → Story Breakdown → Code Generation → PR")
    
    workflow_start = datetime.now()
    
    try:
        # Step 1: Initialize Projektledare
        print_step("Step 1: Initialize Projektledare with GitHub monitoring")
        from agents.projektledare import create_projektledare
        
        projektledare = create_projektledare()
        print_success("Projektledare initialized and ready")
        
        # Step 2: Monitor for new features
        print_step("Step 2: Scanning GitHub for new feature requests")
        
        # Get all feature requests (including any new ones)
        feature_requests = await projektledare.github_comm.process_new_features()
        
        if not feature_requests:
            print_info("No new feature requests found")
            print("💡 Create a GitHub Issue in jhonnyo88/multi-agent-setup with 'enhancement' and 'ai-team' labels")
            return False
        
        print_success(f"Found {len(feature_requests)} feature requests to process")
        
        # Step 3: Process each feature request
        for i, processed_feature in enumerate(feature_requests):
            feature_request = processed_feature['request']
            analysis = processed_feature['analysis']
            
            print_step(f"Step 3.{i+1}: Processing Feature #{feature_request['number']}")
            print_info(f"Title: {feature_request['title']}")
            print_info(f"Action: {analysis.get('recommendation', {}).get('action', 'unknown')}")
            
            if analysis.get('recommendation', {}).get('action') == 'approve':
                print_success("Feature approved by AI analysis!")
                
                # Step 4: Verify story breakdown was created
                if 'stories' in processed_feature:
                    stories = processed_feature['stories']
                    print_success(f"Story breakdown created: {len(stories)} stories")
                    
                    for story in stories:
                        print_info(f"  📄 {story['story_id']}: {story['title']} → {story['assigned_agent']}")
                
                # Step 5: Check if code was generated
                print_step("Step 4: Checking if code generation started")
                
                # Monitor team progress
                if projektledare.agent_coordinator:
                    team_status = await projektledare.monitor_team_progress()
                    active_stories = team_status.get('team_overview', {}).get('active_stories', 0)
                    print_success(f"Team coordination active: {active_stories} stories in progress")
                else:
                    print_info("Team coordination in fallback mode")
                
                # Step 6: Check Git operations
                print_step("Step 5: Checking Git operations in product repo")
                
                product_repo_path = Path("C:/Users/jcols/Documents/diginativa-game")
                if product_repo_path.exists():
                    print_success(f"Product repo accessible: {product_repo_path}")
                    
                    # Check for new branches
                    try:
                        import git
                        repo = git.Repo(product_repo_path)
                        branches = [branch.name for branch in repo.heads]
                        feature_branches = [b for b in branches if 'feature/' in b and 'STORY' in b]
                        
                        if feature_branches:
                            print_success(f"Found feature branches: {feature_branches}")
                        else:
                            print_info("No feature branches found yet (may still be processing)")
                            
                    except Exception as e:
                        print_info(f"Could not check branches: {e}")
                else:
                    print_error(f"Product repo not found at: {product_repo_path}")
                
                # Step 7: Summary
                print_step("Step 6: Workflow Summary")
                
                workflow_duration = datetime.now() - workflow_start
                print_success(f"Workflow completed in {workflow_duration.total_seconds():.1f} seconds")
                
                print_info("✅ Expected results:")
                print_info("  1. GitHub Issue analyzed and commented")
                print_info("  2. Story breakdown issues created")
                print_info("  3. AI team working on implementation")
                print_info("  4. Feature branch created in diginativa-game repo")
                print_info("  5. Pull Request created when code is ready")
                
                print_info("🔍 Manual verification steps:")
                print_info("  1. Check GitHub Issue for AI analysis comment")
                print_info("  2. Look for new story issues in the repo")
                print_info("  3. Check diginativa-game repo for feature branch")
                print_info("  4. Monitor for Pull Request creation")
                
                return True
            else:
                action = analysis.get('recommendation', {}).get('action', 'unknown')
                reasoning = analysis.get('recommendation', {}).get('reasoning', 'No reasoning provided')
                print_info(f"Feature not approved: {action}")
                print_info(f"Reasoning: {reasoning}")
        
        return True
        
    except Exception as e:
        print_error(f"Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def monitor_progress_continuously():
    """Continuously monitor team progress for real-time updates."""
    
    print_section("Continuous Progress Monitoring")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        from agents.projektledare import create_projektledare
        projektledare = create_projektledare()
        
        import asyncio
        
        while True:
            try:
                # Check team progress
                if projektledare.agent_coordinator:
                    team_status = await projektledare.monitor_team_progress()
                    
                    active_stories = team_status.get('team_overview', {}).get('active_stories', 0)
                    completed_stories = team_status.get('team_overview', {}).get('completed_stories', 0)
                    
                    print(f"📊 Team Status: {active_stories} active, {completed_stories} completed")
                    
                    # Show story details
                    for story_detail in team_status.get('story_details', []):
                        story_id = story_detail['story_id']
                        status = story_detail['overall_status']
                        progress = story_detail['completion_percentage']
                        
                        print(f"   📄 {story_id}: {status} ({progress:.0%})")
                
                # Check for new GitHub activity
                print("🔍 Checking for new GitHub activity...")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
                await asyncio.sleep(10)  # Wait shorter on error
                
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # Continuous monitoring mode
        asyncio.run(monitor_progress_continuously())
    else:
        # Single workflow test
        success = asyncio.run(test_real_workflow())
        
        if success:
            print("\n🎉 Real workflow test completed!")
            print("\n💡 Next steps:")
            print("   1. Verify results manually in GitHub")
            print("   2. Run 'python test_real_workflow.py monitor' for continuous monitoring")
            print("   3. Check diginativa-game repo for generated code")
        else:
            print("\n❌ Workflow test had issues - check the output above")
            sys.exit(1)