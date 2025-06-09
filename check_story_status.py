#!/usr/bin/env python3
"""
Check Story Status and Trigger Implementation
============================================

Checks why stories aren't being implemented and triggers implementation.
"""

import asyncio
from datetime import datetime

def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"🔍 {title}")
    print(f"{'='*70}")

def print_step(step: str):
    print(f"\n🔹 {step}")

def print_success(message: str):
    print(f"✅ {message}")

def print_info(message: str):
    print(f"ℹ️  {message}")

def print_error(message: str):
    print(f"❌ {message}")

async def check_story_delegation_status():
    """Check why stories aren't being implemented."""
    
    print_section("Story Implementation Status Check")
    
    try:
        # Step 1: Initialize Projektledare with coordination
        print_step("Step 1: Initialize Team Coordination")
        
        from agents.projektledare import create_projektledare
        projektledare = create_projektledare()
        
        if projektledare.agent_coordinator:
            print_success("Agent coordinator is available")
            
            # Get team status
            team_status = await projektledare.monitor_team_progress()
            
            print_info(f"Active stories: {team_status.get('team_overview', {}).get('active_stories', 0)}")
            print_info(f"Completed stories: {team_status.get('team_overview', {}).get('completed_stories', 0)}")
            print_info(f"Queued tasks: {team_status.get('team_overview', {}).get('queued_tasks', 0)}")
            
        else:
            print_error("Agent coordinator not available - this explains why no implementation started")
        
        # Step 2: Check for created GitHub stories
        print_step("Step 2: Check GitHub Story Issues")
        
        github_comm = projektledare.github_comm
        ai_repo = github_comm.github.ai_repo
        
        # Find story issues
        story_issues = []
        for issue in ai_repo.get_issues(state='open'):
            if '[STORY]' in issue.title:
                story_issues.append(issue)
                print_info(f"Found story: #{issue.number} - {issue.title}")
        
        print_success(f"Found {len(story_issues)} story issues")
        
        # Step 3: Manual delegation test
        print_step("Step 3: Manual Story Delegation Test")
        
        if story_issues:
            # Take the first story (UX Specification)
            first_story = story_issues[0]
            print_info(f"Testing delegation of: {first_story.title}")
            
            # Convert GitHub issue to story format
            story_data = {
                "story_id": "STORY-002-001",  # Extract from title or use manual
                "title": first_story.title.replace("[STORY] ", ""),
                "description": first_story.body[:200] + "..." if first_story.body else "UX Specification",
                "story_type": "specification",
                "assigned_agent": "speldesigner",
                "acceptance_criteria": [
                    "UX specification document created",
                    "Design principles validated",
                    "Acceptance criteria defined"
                ],
                "estimated_effort": "Medium",
                "user_value": "Anna gets a well-designed interface",
                "design_principles_addressed": ["Pedagogik Framför Allt", "Respekt för Tid"]
            }
            
            # Try to delegate manually
            print_info("Attempting manual delegation...")
            
            if projektledare.agent_coordinator:
                try:
                    await projektledare.agent_coordinator.delegate_story(story_data)
                    print_success("✅ Story delegated successfully!")
                    
                    # Check status immediately after
                    await asyncio.sleep(2)
                    
                    story_status = projektledare.agent_coordinator.get_story_status("STORY-002-001")
                    if story_status:
                        print_success(f"Story status: {story_status['overall_status']}")
                        print_info(f"Current phase: {story_status['current_phase']}")
                        print_info(f"Progress: {story_status['completion_percentage']:.0%}")
                    
                except Exception as e:
                    print_error(f"Manual delegation failed: {e}")
            else:
                print_error("Cannot delegate - coordinator not available")
        
        return True
        
    except Exception as e:
        print_error(f"Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def trigger_story_implementation():
    """Trigger implementation of all created stories."""
    
    print_section("Trigger Story Implementation")
    
    try:
        from agents.projektledare import create_projektledare
        projektledare = create_projektledare()
        
        # Step 1: Get all story issues from GitHub
        print_step("Step 1: Collect All Story Issues")
        
        github_comm = projektledare.github_comm
        ai_repo = github_comm.github.ai_repo
        
        story_issues = []
        for issue in ai_repo.get_issues(state='open'):
            if '[STORY]' in issue.title and 'STORY-002-' in issue.title:
                story_issues.append(issue)
        
        print_info(f"Found {len(story_issues)} stories from Feature #2")
        
        # Step 2: Convert to story format and delegate
        print_step("Step 2: Delegate All Stories")
        
        stories_to_delegate = []
        
        for i, issue in enumerate(story_issues, 1):
            # Extract story info from GitHub issue
            title = issue.title.replace("[STORY] ", "")
            
            # Determine agent and type based on title
            if "UX Specification" in title:
                assigned_agent = "speldesigner"
                story_type = "specification"
            elif "Backend API" in title:
                assigned_agent = "utvecklare"
                story_type = "backend"
            elif "React Component" in title:
                assigned_agent = "utvecklare"
                story_type = "frontend"
            elif "Automated Tests" in title:
                assigned_agent = "testutvecklare"
                story_type = "testing"
            elif "QA Testing" in title:
                assigned_agent = "qa_testare"
                story_type = "qa"
            else:
                assigned_agent = "utvecklare"
                story_type = "full_feature"
            
            story_data = {
                "story_id": f"STORY-002-00{i}",
                "title": title,
                "description": issue.body[:200] + "..." if issue.body else f"Implementation of {title}",
                "story_type": story_type,
                "assigned_agent": assigned_agent,
                "acceptance_criteria": [
                    "Implementation completed according to specification",
                    "Code follows architecture principles",
                    "All tests pass"
                ],
                "estimated_effort": "Medium",
                "user_value": "Professional welcome page for Anna",
                "design_principles_addressed": ["Pedagogik Framför Allt", "Respekt för Tid"]
            }
            
            stories_to_delegate.append(story_data)
            print_info(f"  📄 {story_data['story_id']}: {title} → {assigned_agent}")
        
        # Step 3: Delegate all stories
        if projektledare.agent_coordinator and stories_to_delegate:
            print_step("Step 3: Delegating Stories to AI Team")
            
            delegation_result = await projektledare.delegate_stories_to_team(stories_to_delegate)
            
            if delegation_result['coordination_active']:
                print_success(f"✅ Delegated {len(delegation_result['delegated_stories'])} stories!")
                print_info(f"Failed: {len(delegation_result['failed_delegations'])}")
                
                # Step 4: Monitor progress for a bit
                print_step("Step 4: Initial Progress Check")
                
                await asyncio.sleep(5)  # Give agents time to start
                
                team_status = await projektledare.monitor_team_progress()
                active_stories = team_status.get('team_overview', {}).get('active_stories', 0)
                
                print_success(f"🎯 Team now has {active_stories} active stories!")
                
                if active_stories > 0:
                    print_info("✨ Implementation has started!")
                    print_info("💡 Run continuous monitoring to see progress:")
                    print_info("   python test_real_workflow.py monitor")
                else:
                    print_info("⏳ Stories delegated but not yet active - may take a few moments")
                
            else:
                print_error("Delegation failed - coordination not active")
        else:
            print_error("Cannot delegate - no coordinator or no stories")
        
        return True
        
    except Exception as e:
        print_error(f"Implementation trigger failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_full_implementation_cycle():
    """Run a complete implementation cycle for one story."""
    
    print_section("Full Implementation Cycle Test")
    
    try:
        # Step 1: Create enhanced utvecklare directly
        print_step("Step 1: Test Direct Code Generation")
        
        from agents.utvecklare import create_enhanced_utvecklare_agent
        
        utvecklare = create_enhanced_utvecklare_agent()
        
        # Create story data for the UX specification
        story_data = {
            "story_id": "STORY-002-001",
            "title": "Professional Welcome Landing Page UX Specification",
            "description": "Create UX specification for DigiNativa welcome landing page that serves Anna's needs",
            "user_value": "Anna gets a professional introduction to the learning platform",
            "assigned_agent": "speldesigner",
            "story_type": "specification"
        }
        
        print_info("Testing Utvecklare implementation...")
        result = await utvecklare.implement_story_from_spec(story_data)
        
        if result.get("implementation_status") == "completed":
            print_success("✅ Code generation completed!")
            print_info(f"Backend files: {len(result.get('backend_files', []))}")
            print_info(f"Frontend files: {len(result.get('frontend_files', []))}")
            print_info(f"Git commit: {result.get('git_commit', 'N/A')}")
            print_info(f"Pull request: {result.get('pull_request', 'N/A')}")
            
            # Check if files were actually created
            print_step("Step 2: Verify Generated Files")
            
            import os
            product_repo = r"C:\Users\jcols\Documents\diginativa-game"
            
            # Check for backend files
            backend_path = os.path.join(product_repo, "backend", "app", "api")
            if os.path.exists(backend_path):
                backend_files = [f for f in os.listdir(backend_path) if f.endswith('.py')]
                print_success(f"Backend files found: {len(backend_files)}")
                for file in backend_files:
                    print_info(f"  📄 {file}")
            
            # Check for frontend files  
            frontend_path = os.path.join(product_repo, "frontend", "src", "components")
            if os.path.exists(frontend_path):
                frontend_files = [f for f in os.listdir(frontend_path) if f.endswith('.tsx')]
                print_success(f"Frontend files found: {len(frontend_files)}")
                for file in frontend_files:
                    print_info(f"  📄 {file}")
            
            # Check for feature branches
            print_step("Step 3: Check Git Branches")
            
            try:
                import git
                repo = git.Repo(product_repo)
                branches = [branch.name for branch in repo.heads]
                feature_branches = [b for b in branches if 'feature/' in b or 'STORY' in b]
                
                if feature_branches:
                    print_success(f"Feature branches found: {feature_branches}")
                else:
                    print_info("No feature branches found yet")
            except Exception as e:
                print_info(f"Could not check branches: {e}")
            
            return True
        else:
            print_error(f"Code generation failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print_error(f"Full implementation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            success = asyncio.run(check_story_delegation_status())
        elif sys.argv[1] == "trigger":
            success = asyncio.run(trigger_story_implementation())
        elif sys.argv[1] == "implement":
            success = asyncio.run(run_full_implementation_cycle())
        else:
            print("Usage: python check_story_status.py [status|trigger|implement]")
            sys.exit(1)
    else:
        # Default: check status
        success = asyncio.run(check_story_delegation_status())
    
    if success:
        print("\n🎉 Check completed successfully!")
    else:
        print("\n❌ Check found issues")
        
    print("\n💡 Available commands:")
    print("   python check_story_status.py status    # Check delegation status")
    print("   python check_story_status.py trigger   # Trigger story delegation")
    print("   python check_story_status.py implement # Test direct implementation")