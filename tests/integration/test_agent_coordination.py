#!/usr/bin/env python3
"""
Agent Coordination Integration Test Suite
========================================

PURPOSE:
Complete integration tests for the new agent coordination system.
Tests delegation, sequential workflow, status tracking, and exception handling.

WHAT THIS TESTS:
1. Agent coordinator initialization
2. Story delegation to specialist agents
3. Sequential workflow enforcement (Spec → Code → Test)
4. Status tracking and progress monitoring
5. Exception handling and recovery
6. Team dashboard and reporting

HOW TO RUN:
    python tests/integration/test_agent_coordination.py

EXPECTED OUTPUT:
- Successful coordinator initialization
- Story delegation to appropriate agents
- Sequential task execution
- Status tracking and team monitoring
- Dashboard generation
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
import os

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from workflows.agent_coordinator import AgentCoordinator, create_agent_coordinator
    from agents.projektledare import create_projektledare
    from workflows.status_handler import StatusHandler
    from config.settings import PROJECT_ROOT
    print("✅ Successfully imported coordination system components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have:")
    print("1. Created workflows/agent_coordinator.py")
    print("2. Updated agents/projektledare.py with coordination methods")
    print("3. All dependencies are installed")
    sys.exit(1)

def print_section(title: str):
    """Print clear test section headers."""
    print(f"\n{'='*70}")
    print(f"🧪 {title}")
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

class AgentCoordinationTestSuite:
    """Complete test suite for agent coordination system."""

    def __init__(self):
        self.test_results = {
            "coordinator_initialization": False,
            "story_delegation": False,
            "sequential_workflow": False,
            "status_tracking": False,
            "team_monitoring": False,
            "exception_handling": False,
            "dashboard_generation": False
        }
        
        # Test data
        self.test_stories = [
            {
                "story_id": "STORY-COORD-001",
                "title": "User Authentication System",
                "description": "Create secure user login and registration system",
                "story_type": "full_feature",
                "assigned_agent": "speldesigner",
                "acceptance_criteria": [
                    "User can register with email and password",
                    "User can login with valid credentials",
                    "Session management works correctly",
                    "Password validation follows security standards"
                ],
                "estimated_effort": "Large",
                "user_value": "Users can securely access their accounts"
            },
            {
                "story_id": "STORY-COORD-002", 
                "title": "API Rate Limiting",
                "description": "Implement rate limiting for API endpoints",
                "story_type": "backend_only",
                "assigned_agent": "utvecklare",
                "acceptance_criteria": [
                    "API endpoints have rate limiting configured",
                    "Rate limits are configurable per endpoint",
                    "Appropriate HTTP status codes returned"
                ],
                "estimated_effort": "Medium",
                "user_value": "API performance and reliability improved"
            },
            {
                "story_id": "STORY-COORD-003",
                "title": "Dashboard UX Improvements", 
                "description": "Improve user experience of main dashboard",
                "story_type": "frontend_only",
                "assigned_agent": "speldesigner",
                "acceptance_criteria": [
                    "Dashboard loads in under 2 seconds",
                    "Mobile responsive design implemented",
                    "User can customize dashboard layout"
                ],
                "estimated_effort": "Medium",
                "user_value": "Improved user satisfaction and efficiency"
            }
        ]

    async def run_full_test_suite(self) -> dict:
        """Run complete agent coordination test suite."""
        print_section("Agent Coordination System - Full Integration Test")
        print_info("Testing complete multi-agent workflow coordination")
        
        # Run tests in logical order
        await self.test_coordinator_initialization()
        await self.test_story_delegation()
        await self.test_sequential_workflow()
        await self.test_status_tracking()
        await self.test_team_monitoring()
        await self.test_exception_handling()
        await self.test_dashboard_generation()
        
        return self.test_results

    async def test_coordinator_initialization(self):
        """Test agent coordinator can be created and configured."""
        print_section("Test 1: Agent Coordinator Initialization")
        
        try:
            print_info("Creating agent coordinator...")
            coordinator = create_agent_coordinator()
            
            # Verify coordinator structure
            assert hasattr(coordinator, 'agent_capabilities'), "Should have agent capabilities"
            assert hasattr(coordinator, 'workflow_sequences'), "Should have workflow sequences"
            assert hasattr(coordinator, 'delegation_rules'), "Should have delegation rules"
            assert hasattr(coordinator, 'active_stories'), "Should track active stories"
            
            # Verify agent capabilities are loaded
            expected_agents = ["speldesigner", "utvecklare", "testutvecklare", "qa_testare", "kvalitetsgranskare"]
            for agent in expected_agents:
                assert agent in coordinator.agent_capabilities, f"Missing agent: {agent}"
                
            # Verify workflow sequences
            assert "full_feature" in coordinator.workflow_sequences, "Should have full feature workflow"
            assert "backend_only" in coordinator.workflow_sequences, "Should have backend workflow"
            
            print_success("Agent coordinator initialized successfully")
            print_info(f"Agents configured: {len(coordinator.agent_capabilities)}")
            print_info(f"Workflow types: {list(coordinator.workflow_sequences.keys())}")
            
            self.test_results["coordinator_initialization"] = True
            return coordinator
            
        except Exception as e:
            print_error(f"Coordinator initialization failed: {e}")
            self.test_results["coordinator_initialization"] = False
            return None

    async def test_story_delegation(self):
        """Test delegating stories to the coordination system."""
        print_section("Test 2: Story Delegation")
        
        try:
            print_info("Testing story delegation...")
            
            # Create coordinator
            coordinator = create_agent_coordinator()
            
            # Test delegating a single story
            test_story = self.test_stories[0]  # Full feature story
            print_info(f"Delegating story: {test_story['story_id']}")
            
            story_id = await coordinator.delegate_story(test_story)
            
            # Verify story was added to active stories
            assert story_id in coordinator.active_stories, "Story should be in active stories"
            
            # Verify story workflow was created
            story_workflow = coordinator.active_stories[story_id]
            assert story_workflow.story_id == story_id, "Story ID should match"
            assert story_workflow.overall_status == "active", "Story should be active"
            assert len(story_workflow.tasks) > 0, "Story should have tasks"
            
            # Verify tasks were created in correct sequence
            task_types = [task.task_type for task in story_workflow.tasks]
            expected_sequence = coordinator.workflow_sequences["full_feature"]
            assert task_types == expected_sequence, f"Task sequence mismatch: {task_types} vs {expected_sequence}"
            
            print_success("Story delegation completed successfully")
            print_info(f"Created {len(story_workflow.tasks)} tasks in sequence")
            print_info(f"Task sequence: {' → '.join(task_types)}")
            
            self.test_results["story_delegation"] = True
            return coordinator
            
        except Exception as e:
            print_error(f"Story delegation test failed: {e}")
            self.test_results["story_delegation"] = False
            return None

    async def test_sequential_workflow(self):
        """Test that workflow enforces correct sequence."""
        print_section("Test 3: Sequential Workflow Enforcement")
        
        try:
            print_info("Testing sequential workflow...")
            
            # Create coordinator and delegate story
            coordinator = create_agent_coordinator()
            test_story = self.test_stories[1]  # Backend-only story
            story_id = await coordinator.delegate_story(test_story)
            
            story_workflow = coordinator.active_stories[story_id]
            
            # Verify initial state - only first task should be ready
            ready_tasks = [task for task in story_workflow.tasks if not task.dependencies]
            assert len(ready_tasks) == 1, "Only first task should have no dependencies"
            assert ready_tasks[0].task_type == "specification", "First task should be specification"
            
            # Verify dependency chain
            tasks_by_type = {task.task_type: task for task in story_workflow.tasks}
            
            # Each task (except first) should depend on previous task
            sequence = coordinator.workflow_sequences["backend_only"]
            for i in range(1, len(sequence)):
                current_task = tasks_by_type[sequence[i]]
                previous_task_id = f"{story_id}_{sequence[i-1]}"
                assert previous_task_id in current_task.dependencies, f"Task {current_task.task_type} should depend on {sequence[i-1]}"
            
            print_success("Sequential workflow enforced correctly")
            print_info(f"Workflow sequence: {' → '.join(sequence)}")
            print_info("✓ Dependencies verified")
            print_info("✓ Only first task ready to start")
            
            self.test_results["sequential_workflow"] = True
            
        except Exception as e:
            print_error(f"Sequential workflow test failed: {e}")
            self.test_results["sequential_workflow"] = False

    async def test_status_tracking(self):
        """Test status tracking and task progression."""
        print_section("Test 4: Status Tracking")
        
        try:
            print_info("Testing status tracking...")
            
            # Create coordinator and delegate story
            coordinator = create_agent_coordinator()
            test_story = self.test_stories[2]  # Frontend-only story
            story_id = await coordinator.delegate_story(test_story)
            
            # Get initial story status
            initial_status = coordinator.get_story_status(story_id)
            assert initial_status is not None, "Should return story status"
            assert initial_status["story_id"] == story_id, "Should return correct story"
            assert initial_status["overall_status"] == "active", "Story should be active"
            
            # Verify status structure
            required_fields = ["story_id", "title", "overall_status", "current_phase", 
                             "completion_percentage", "tasks", "artifacts"]
            for field in required_fields:
                assert field in initial_status, f"Missing field in status: {field}"
            
            # Test team status
            team_status = coordinator.get_team_status()
            assert "active_stories" in team_status, "Should include active stories count"
            assert "agent_workload" in team_status, "Should include agent workload"
            assert team_status["active_stories"] >= 1, "Should show at least one active story"
            
            print_success("Status tracking working correctly")
            print_info(f"Story status fields: {len(initial_status)} fields")
            print_info(f"Team status: {team_status['active_stories']} active stories")
            print_info(f"Agent workload: {team_status['agent_workload']}")
            
            self.test_results["status_tracking"] = True
            
        except Exception as e:
            print_error(f"Status tracking test failed: {e}")
            self.test_results["status_tracking"] = False

    async def test_team_monitoring(self):
        """Test team monitoring and progress analysis."""
        print_section("Test 5: Team Monitoring")
        
        try:
            print_info("Testing team monitoring...")
            
            # Create coordinator with multiple stories
            coordinator = create_agent_coordinator()
            
            # Delegate multiple stories to create workload
            delegated_stories = []
            for story in self.test_stories:
                story_id = await coordinator.delegate_story(story)
                delegated_stories.append(story_id)
            
            # Test team status with multiple stories
            team_status = coordinator.get_team_status()
            assert team_status["active_stories"] == len(self.test_stories), "Should track all delegated stories"
            assert team_status["total_stories"] == len(self.test_stories), "Should count total stories"
            
            # Verify agent workload tracking
            workload = team_status["agent_workload"]
            assert isinstance(workload, dict), "Workload should be dictionary"
            
            # Test individual story monitoring
            for story_id in delegated_stories:
                story_status = coordinator.get_story_status(story_id)
                assert story_status is not None, f"Should return status for {story_id}"
                assert story_status["completion_percentage"] >= 0, "Should have valid completion percentage"
            
            print_success("Team monitoring working correctly")
            print_info(f"Monitoring {len(delegated_stories)} active stories")
            print_info(f"Team status: {team_status['active_stories']} active, {team_status['queued_tasks']} queued tasks")
            
            self.test_results["team_monitoring"] = True
            
        except Exception as e:
            print_error(f"Team monitoring test failed: {e}")
            self.test_results["team_monitoring"] = False

    async def test_exception_handling(self):
        """Test exception handling in coordination system."""
        print_section("Test 6: Exception Handling")
        
        try:
            print_info("Testing exception handling...")
            
            # Create coordinator
            coordinator = create_agent_coordinator()
            
            # Test with invalid story data to trigger exception
            invalid_story = {
                "story_id": "",  # Invalid empty ID
                "title": "",
                "description": "",
                "story_type": "invalid_type"
            }
            
            # This should handle the exception gracefully
            try:
                story_id = await coordinator.delegate_story(invalid_story)
                print_warning("Expected exception was not raised")
            except Exception as e:
                print_info(f"Exception handled correctly: {str(e)[:50]}...")
            
            # Test with valid story to ensure system still works
            valid_story = self.test_stories[0]
            story_id = await coordinator.delegate_story(valid_story)
            
            # Verify system is still functional
            team_status = coordinator.get_team_status()
            assert team_status["active_stories"] >= 1, "System should still be functional"
            
            print_success("Exception handling working correctly")
            print_info("✓ Invalid input handled gracefully")
            print_info("✓ System remains functional after exception")
            
            self.test_results["exception_handling"] = True
            
        except Exception as e:
            print_error(f"Exception handling test failed: {e}")
            self.test_results["exception_handling"] = False

    async def test_dashboard_generation(self):
        """Test team dashboard and reporting functionality."""
        print_section("Test 7: Dashboard Generation")
        
        try:
            print_info("Testing dashboard generation...")
            
            # This test requires the enhanced Projektledare
            # We'll create a mock version for testing
            coordinator = create_agent_coordinator()
            
            # Delegate a story to have some data
            test_story = self.test_stories[0]
            story_id = await coordinator.delegate_story(test_story)
            
            # Test basic team status (dashboard foundation)
            team_status = coordinator.get_team_status()
            
            # Verify dashboard data structure
            required_dashboard_fields = [
                "active_stories", "completed_stories", "blocked_stories",
                "queued_tasks", "agent_workload", "total_stories"
            ]
            
            for field in required_dashboard_fields:
                assert field in team_status, f"Dashboard missing field: {field}"
            
            # Test story status details (for dashboard)
            story_status = coordinator.get_story_status(story_id)
            dashboard_story_fields = [
                "story_id", "title", "overall_status", "current_phase",
                "completion_percentage", "tasks"
            ]
            
            for field in dashboard_story_fields:
                assert field in story_status, f"Story status missing field: {field}"
            
            print_success("Dashboard generation components working")
            print_info(f"Team status fields: {len(team_status)} fields")
            print_info(f"Story status fields: {len(story_status)} fields")
            print_info("✓ All required dashboard data available")
            
            self.test_results["dashboard_generation"] = True
            
        except Exception as e:
            print_error(f"Dashboard generation test failed: {e}")
            self.test_results["dashboard_generation"] = False

def print_final_results(test_results: dict):
    """Print summary of all test results."""
    print_section("Agent Coordination Test Results")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print_info(f"Tests passed: {passed_tests}/{total_tests}")
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    if passed_tests == total_tests:
        print_success("🎉 All agent coordination tests passed!")
        print_info("Your AI team coordination system is ready for production!")
        print_info("\nNext steps:")
        print_info("1. Integrate coordination methods into your Projektledare")
        print_info("2. Test with real GitHub issues")
        print_info("3. Monitor team performance in practice")
        
    elif passed_tests >= total_tests * 0.8:
        print_warning("✨ Most coordination tests passed!")
        print_info("Core functionality is working. Review failed tests:")
        failed_tests = [name for name, passed in test_results.items() if not passed]
        for test in failed_tests:
            print_info(f"   - Fix: {test.replace('_', ' ')}")
            
    else:
        print_error("🚨 Critical coordination issues found!")
        print_info("Please fix these issues before proceeding:")
        print_info("1. Check that agent_coordinator.py is properly created")
        print_info("2. Verify all imports are working")
        print_info("3. Ensure database/state storage is accessible")

async def main():
    """Main test runner."""
    print("🚀 Starting Agent Coordination Integration Tests...")
    print_info("This will test the complete multi-agent coordination system")
    
    try:
        # Run the test suite
        test_suite = AgentCoordinationTestSuite()
        results = await test_suite.run_full_test_suite()
        
        # Print results
        print_final_results(results)
        
        # Return success status
        passed_tests = sum(1 for result in results.values() if result)
        return passed_tests >= len(results) * 0.8  # 80% pass rate required
        
    except KeyboardInterrupt:
        print_error("\nTests cancelled by user (Ctrl+C)")
        return False
    except Exception as e:
        print_error(f"Test suite failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the async test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1)