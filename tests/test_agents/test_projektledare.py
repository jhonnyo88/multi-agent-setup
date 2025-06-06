#!/usr/bin/env python3
"""
Basic Test Script for Projektledare Agent
========================================

PURPOSE:
Simple test script to verify that the Projektledare agent can be initialized
and can perform basic feature analysis. This helps us validate that all 
dependencies are working before building out the full workflow.

WHAT THIS TESTS:
1. Agent initialization with all required dependencies
2. Feature analysis workflow with mock GitHub issue data
3. Status handler integration and logging
4. Exception handling system basic functionality
5. Story breakdown logic

HOW TO RUN:
    python test_projektledare_basic.py

EXPECTED OUTPUT:
- Successful agent initialization
- Feature analysis JSON response
- Status logging confirmation
- Story breakdown with assigned agents

This is a BEGINNER-FRIENDLY test script with detailed output and error handling.
"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to Python path so we can import our modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import our project modules
try:
    from agents.projektledare import create_projektledare, ProjektledareAgent
    from workflows.status_handler import StatusHandler
    from workflows.exception_handler import ExceptionHandler
    print("✅ Successfully imported all required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def print_section(title: str):
    """Helper function to print clear section headers."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message: str):
    """Helper function to print success messages."""
    print(f"✅ {message}")

def print_error(message: str):
    """Helper function to print error messages."""
    print(f"❌ {message}")

def print_info(message: str):
    """Helper function to print info messages."""
    print(f"ℹ️  {message}")

async def test_basic_initialization():
    """
    Test 1: Basic Agent Initialization
    
    This verifies that we can create a Projektledare agent without errors.
    """
    print_section("Test 1: Basic Agent Initialization")
    
    try:
        print_info("Creating Projektledare agent...")
        projektledare = create_projektledare()
        
        # Check that we got a valid agent object
        if isinstance(projektledare, ProjektledareAgent):
            print_success("Projektledare agent created successfully")
            print_info(f"Agent type: {type(projektledare)}")
            print_info(f"Domain context: {projektledare.domain_context['primary_domain']}")
            print_info(f"Target user: {projektledare.domain_context['target_user']}")
            return projektledare
        else:
            print_error(f"Expected ProjektledareAgent, got {type(projektledare)}")
            return None
            
    except Exception as e:
        print_error(f"Failed to create Projektledare: {e}")
        print_info("This usually means:")
        print_info("- Missing environment variables (check .env file)")
        print_info("- Missing dependencies (run: pip install -r requirements.txt)")
        print_info("- Database initialization issues")
        return None

async def test_status_handler():
    """
    Test 2: Status Handler Functionality
    
    This verifies that the status handling system works correctly.
    """
    print_section("Test 2: Status Handler System")
    
    try:
        print_info("Creating status handler...")
        status_handler = StatusHandler()
        
        # Test reporting a success status
        print_info("Testing success status reporting...")
        success_result = status_handler.report_status(
            agent_name="projektledare",
            status_code="FEATURE_ANALYZED",
            payload={
                "test": True,
                "feature_id": "TEST-001",
                "analysis_result": "approved"
            },
            story_id="TEST-STORY-001"
        )
        
        if success_result:
            print_success("Success status reported correctly")
        else:
            print_error("Failed to report success status")
            return False
        
        # Test retrieving the status
        print_info("Testing status retrieval...")
        latest_status = status_handler.get_latest_status("projektledare")
        
        if latest_status and latest_status["status_code"] == "FEATURE_ANALYZED":
            print_success("Status retrieved successfully")
            print_info(f"Retrieved status: {latest_status['status_code']}")
            print_info(f"Payload keys: {list(latest_status['payload'].keys())}")
        else:
            print_error("Failed to retrieve status or unexpected status")
            return False
        
        # Test error status recognition
        print_info("Testing error status recognition...")
        is_success = status_handler.is_success_status("LYCKAD_SPEC_LEVERERAD")
        is_error = status_handler.is_error_status("FEL_SPEC_TVETYDIG_U")
        
        if is_success and is_error:
            print_success("Status code recognition working correctly")
        else:
            print_error("Status code recognition failed")
            return False
            
        return True
        
    except Exception as e:
        print_error(f"Status handler test failed: {e}")
        return False

async def test_feature_analysis(projektledare: ProjektledareAgent):
    """
    Test 3: Feature Analysis Workflow
    
    This tests the core functionality of analyzing a GitHub issue.
    """
    print_section("Test 3: Feature Analysis Workflow")
    
    # Create a realistic mock GitHub issue for DigiNativa
    mock_github_issue = {
        "number": 123,
        "title": "Add user progress tracking to game",
        "body": """
        ## Feature Description
        Users should be able to see their learning progress through the digitalization strategy game.
        
        ## User Story
        As Anna (public sector employee), I want to see my progress through the game so that I can 
        understand how much I've learned and what topics I still need to cover.
        
        ## Acceptance Criteria
        - [ ] Display progress bar showing completion percentage
        - [ ] Show which topics have been completed
        - [ ] Indicate time spent learning
        - [ ] Allow user to resume from where they left off
        - [ ] Progress should persist between sessions
        
        ## Technical Notes
        - Should integrate with existing user authentication
        - Progress data should be stored securely
        - Must be responsive for mobile devices
        - Should follow our 5 design principles
        """,
        "labels": [
            {"name": "feature"}, 
            {"name": "enhancement"},
            {"name": "user-experience"}
        ],
        "user": {"login": "test-user"},
        "state": "open",
        "created_at": "2024-12-20T10:00:00Z"
    }
    
    try:
        print_info("Starting feature analysis...")
        print_info(f"Analyzing issue: '{mock_github_issue['title']}'")
        
        # This is the main test - can the Projektledare analyze a feature request?
        analysis_result = await projektledare.analyze_feature_request(mock_github_issue)
        
        if analysis_result and isinstance(analysis_result, dict):
            print_success("Feature analysis completed successfully!")
            
            # Print a summary of the analysis (user-friendly format)
            print_info("Analysis Summary:")
            
            if "dna_alignment" in analysis_result:
                dna = analysis_result["dna_alignment"]
                print_info(f"  Vision/Mission Aligned: {dna.get('vision_mission_aligned', 'unknown')}")
                print_info(f"  Target Audience Served: {dna.get('target_audience_served', 'unknown')}")
                print_info(f"  Design Principles Compatible: {dna.get('design_principles_compatible', 'unknown')}")
                
                if dna.get("concerns"):
                    print_info(f"  Concerns: {', '.join(dna['concerns'])}")
            
            if "complexity" in analysis_result:
                complexity = analysis_result["complexity"]
                print_info(f"  Estimated Stories: {complexity.get('estimated_stories', 'unknown')}")
                print_info(f"  Required Agents: {', '.join(complexity.get('required_agents', []))}")
                print_info(f"  Complexity Level: {complexity.get('complexity_level', 'unknown')}")
            
            if "recommendation" in analysis_result:
                rec = analysis_result["recommendation"]
                print_info(f"  Recommendation: {rec.get('action', 'unknown')}")
                print_info(f"  Priority: {rec.get('priority', 'unknown')}")
            
            # Show full JSON for debugging (but make it readable)
            print_info("\nFull Analysis (JSON format):")
            print(json.dumps(analysis_result, indent=2, ensure_ascii=False))
            
            return analysis_result
            
        else:
            print_error("Feature analysis failed or returned invalid result")
            print_info(f"Result type: {type(analysis_result)}")
            if analysis_result:
                print_info(f"Result content: {analysis_result}")
            return None
            
    except Exception as e:
        print_error(f"Feature analysis test failed: {e}")
        print_info("This could be due to:")
        print_info("- OpenAI API key issues")
        print_info("- Network connectivity problems") 
        print_info("- Agent configuration errors")
        print_info("- Missing DNA documents")
        return None

async def test_story_breakdown(projektledare: ProjektledareAgent, analysis_result: dict, mock_issue: dict):
    """
    Test 4: Story Breakdown Workflow
    
    This tests whether the Projektledare can break down a feature into implementable stories.
    """
    print_section("Test 4: Story Breakdown Workflow")
    
    # Only run this test if the feature was approved
    if (analysis_result.get("recommendation", {}).get("action") != "approve"):
        print_info("Skipping story breakdown - feature was not approved in analysis")
        print_info(f"Recommendation was: {analysis_result.get('recommendation', {}).get('action')}")
        return True  # This is not a test failure
    
    try:
        print_info("Starting story breakdown...")
        
        stories = await projektledare.create_story_breakdown(analysis_result, mock_issue)
        
        if stories and isinstance(stories, list) and len(stories) > 0:
            print_success(f"Story breakdown completed! Created {len(stories)} stories")
            
            print_info("Generated Stories:")
            for i, story in enumerate(stories, 1):
                print_info(f"  {i}. {story.get('story_id', 'NO-ID')}: {story.get('title', 'No title')}")
                print_info(f"     Assigned to: {story.get('assigned_agent', 'unknown')}")
                print_info(f"     Type: {story.get('story_type', 'unknown')}")
                print_info(f"     Effort: {story.get('estimated_effort', 'unknown')}")
                print_info(f"     Acceptance Criteria: {len(story.get('acceptance_criteria', []))} items")
            
            # Show one full story as example
            if stories:
                print_info(f"\nExample Story Details (Story 1):")
                example_story = stories[0]
                print(json.dumps(example_story, indent=2, ensure_ascii=False))
                
            return stories
            
        else:
            print_error("Story breakdown failed or returned no stories")
            print_info(f"Result: {stories}")
            return None
            
    except Exception as e:
        print_error(f"Story breakdown test failed: {e}")
        return None

async def test_exception_handling():
    """
    Test 5: Exception Handling System
    
    This tests that our exception handling system works correctly.
    """
    print_section("Test 5: Exception Handling System")
    
    try:
        print_info("Creating exception handler...")
        status_handler = StatusHandler()
        exception_handler = ExceptionHandler(status_handler)
        
        # Test handling a specification ambiguity exception
        print_info("Testing Risk 1: Ambiguous Specification handling...")
        
        test_payload = {
            "agent_name": "utvecklare",
            "otydlighet_beskrivning": "API endpoint specification unclear - no authentication method specified",
            "spec_referens": "spec-F-01/STORY-123-001.md#section_3"
        }
        
        resolution = await exception_handler.handle_exception(
            status_code="FEL_SPEC_TVETYDIG_U",
            payload=test_payload,
            story_id="TEST-STORY-001"
        )
        
        if resolution and resolution.handled:
            print_success("Exception handling working correctly")
            print_info(f"Risk type: {resolution.risk_type}")
            print_info(f"Actions taken: {len(resolution.actions_taken)}")
            print_info(f"New tasks created: {len(resolution.new_tasks or [])}")
            print_info(f"Human escalation needed: {resolution.escalate_to_human}")
            
            # Show resolution details
            print_info("Resolution details:")
            for action in resolution.actions_taken:
                print_info(f"  - {action}")
                
            return True
        else:
            print_error("Exception handling failed")
            return False
            
    except Exception as e:
        print_error(f"Exception handling test failed: {e}")
        return False

async def run_all_tests():
    """
    Main test runner that executes all tests in sequence.
    
    This gives us a complete picture of whether the Projektledare system is working.
    """
    print_section("DigiNativa Projektledare - Basic Test Suite")
    print_info("This test verifies that our AI team foundation is working correctly.")
    print_info("Each test builds on the previous one, so we'll stop if any critical test fails.")
    
    test_results = {
        "initialization": False,
        "status_handler": False,
        "feature_analysis": False,
        "story_breakdown": False,
        "exception_handling": False
    }
    
    # Test 1: Basic initialization
    projektledare = await test_basic_initialization()
    if projektledare is None:
        print_error("Critical failure: Cannot create Projektledare agent")
        print_info("Please check your configuration and try again")
        return test_results
    test_results["initialization"] = True
    
    # Test 2: Status handler
    status_ok = await test_status_handler()
    if not status_ok:
        print_error("Critical failure: Status handler not working")
        print_info("This will prevent agent coordination")
        return test_results
    test_results["status_handler"] = True
    
    # Test 3: Feature analysis (this is the big one!)
    analysis_result = await test_feature_analysis(projektledare)
    if analysis_result is None:
        print_error("Feature analysis failed - this is a critical function")
        print_info("Check your OpenAI API key and network connection")
        return test_results
    test_results["feature_analysis"] = True
    
    # Test 4: Story breakdown (only if analysis succeeded)
    if analysis_result:
        stories = await test_story_breakdown(
            projektledare, 
            analysis_result, 
            {
                "number": 123,
                "title": "Add user progress tracking to game"
            }
        )
        if stories is not None:
            test_results["story_breakdown"] = True
    
    # Test 5: Exception handling
    exception_ok = await test_exception_handling()
    if exception_ok:
        test_results["exception_handling"] = True
    
    return test_results

def print_final_results(test_results: dict):
    """Print a summary of all test results."""
    print_section("Test Results Summary")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print_info(f"Tests passed: {passed_tests}/{total_tests}")
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    if passed_tests == total_tests:
        print_success("🎉 All tests passed! Your Projektledare is ready to work!")
        print_info("Next steps:")
        print_info("1. Try creating a real GitHub issue in your repository")
        print_info("2. Run: python scripts/deploy_agents.py")
        print_info("3. Create your first feature request")
    elif passed_tests >= 3:
        print_info("✨ Core functionality is working!")
        print_info("You can start testing with real features, but some advanced features may not work yet.")
    else:
        print_error("🚨 Critical issues found. Please fix the failing tests before proceeding.")
        print_info("Common solutions:")
        print_info("- Check .env file for correct API keys")
        print_info("- Run: pip install -r requirements.txt")
        print_info("- Ensure you're in the project root directory")

def main():
    """
    Main function that runs the test suite.
    
    This is designed to be beginner-friendly with clear output and helpful error messages.
    """
    print("🚀 Starting DigiNativa Projektledare Basic Test Suite...")
    print_info("This will test the core functionality of your AI team setup.")
    
    try:
        # Run the async test suite
        test_results = asyncio.run(run_all_tests())
        print_final_results(test_results)
        
        # Exit with appropriate code
        passed_tests = sum(1 for result in test_results.values() if result)
        if passed_tests >= 3:  # At least core functionality working
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_error("\nTest cancelled by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error during testing: {e}")
        print_info("This might indicate a serious configuration issue.")
        sys.exit(1)

if __name__ == "__main__":
    main()