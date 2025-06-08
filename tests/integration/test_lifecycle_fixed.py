#!/usr/bin/env python3
"""
Fixed Lifecycle Test - Without infinite agent initialization loops
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys
from unittest.mock import MagicMock, patch

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import dependencies
from config.settings import PROJECT_ROOT

def print_section(title: str):
    """Print clear test section headers."""
    print(f"\n{'='*70}")
    print(f"🧪 {title}")
    print(f"{'='*70}")

def print_success(message: str):
    print(f"✅ {message}")

def print_info(message: str):
    print(f"ℹ️  {message}")

def print_error(message: str):
    print(f"❌ {message}")

# Mock fixtures
@patch('workflows.agent_coordinator.create_agent_coordinator')
class TestLifecycleFixed:
    """Fixed lifecycle tests with proper mocking."""
    
    def __init__(self):
        # Mock data for testing
        self.mock_github_issue = {
            "number": 123,
            "title": "Add user progress tracking",
            "body": """
            ## Feature Description
            Users should be able to see their learning progress.
            
            ## Acceptance Criteria
            - [ ] Display progress bar showing completion percentage
            - [ ] Show which topics have been completed
            """,
            "labels": [{"name": "feature"}, {"name": "enhancement"}],
            "user": {"login": "test-user"},
            "state": "open",
            "created_at": "2024-12-20T10:00:00Z"
        }

    @patch('agents.speldesigner.create_speldesigner_agent')
    @patch('agents.utvecklare.create_utvecklare_agent')
    @patch('agents.testutvecklare.create_testutvecklare_agent')
    @patch('agents.qa_testare.create_qa_testare_agent')
    @patch('agents.kvalitetsgranskare.create_kvalitetsgranskare_agent')
    def test_projektledare_initialization(self, mock_coord, *agent_mocks):
        """Test Projektledare initialization without loops."""
        print_section("Test 1: Projektledare Initialization (Fixed)")
        
        try:
            # Mock coordinator to prevent infinite loop
            mock_coord.return_value = MagicMock()
            
            # Mock all agents
            for mock in agent_mocks:
                mock.return_value = MagicMock()
            
            from agents.projektledare import ProjektledareAgent
            
            # Create projektledare - this should not loop now
            projektledare = ProjektledareAgent()
            
            assert projektledare is not None
            assert hasattr(projektledare, 'claude_llm')
            assert hasattr(projektledare, 'agent')
            
            print_success("Projektledare initialized successfully without loops")
            return projektledare
            
        except Exception as e:
            print_error(f"Failed to initialize Projektledare: {e}")
            return None

    async def test_feature_analysis(self, mock_coord):
        """Test feature analysis functionality."""
        print_section("Test 2: Feature Analysis (Fixed)")
        
        try:
            # Mock coordinator
            mock_coord.return_value = MagicMock()
            
            # Import and create projektledare with mocked dependencies
            with patch('agents.speldesigner.create_speldesigner_agent'), \
                 patch('agents.utvecklare.create_utvecklare_agent'), \
                 patch('agents.testutvecklare.create_testutvecklare_agent'), \
                 patch('agents.qa_testare.create_qa_testare_agent'), \
                 patch('agents.kvalitetsgranskare.create_kvalitetsgranskare_agent'):
                
                from agents.projektledare import ProjektledareAgent
                projektledare = ProjektledareAgent()
                
                print_info(f"Analyzing issue: '{self.mock_github_issue['title']}'")
                
                # Test analysis
                analysis_result = await projektledare.analyze_feature_request(self.mock_github_issue)
                
                assert isinstance(analysis_result, dict)
                assert "recommendation" in analysis_result
                
                print_success("Feature analysis completed successfully")
                print_info(f"Recommendation: {analysis_result.get('recommendation', {}).get('action', 'unknown')}")
                
                return analysis_result
                
        except Exception as e:
            print_error(f"Feature analysis failed: {e}")
            return None

    async def test_story_breakdown(self, mock_coord):
        """Test story breakdown creation."""
        print_section("Test 3: Story Breakdown (Fixed)")
        
        try:
            # Mock coordinator
            mock_coord.return_value = MagicMock()
            
            with patch('agents.speldesigner.create_speldesigner_agent'), \
                 patch('agents.utvecklare.create_utvecklare_agent'), \
                 patch('agents.testutvecklare.create_testutvecklare_agent'), \
                 patch('agents.qa_testare.create_qa_testare_agent'), \
                 patch('agents.kvalitetsgranskare.create_kvalitetsgranskare_agent'):
                
                from agents.projektledare import ProjektledareAgent
                projektledare = ProjektledareAgent()
                
                # First get analysis
                analysis_result = await projektledare.analyze_feature_request(self.mock_github_issue)
                
                # Then create stories
                stories = await projektledare.create_story_breakdown(analysis_result, self.mock_github_issue)
                
                assert isinstance(stories, list)
                assert len(stories) > 0
                
                print_success(f"Created {len(stories)} stories successfully")
                for story in stories:
                    print_info(f"  - {story['story_id']}: {story['title']} (→ {story['assigned_agent']})")
                
                return stories
                
        except Exception as e:
            print_error(f"Story breakdown failed: {e}")
            return None

    def test_file_operations(self, mock_coord):
        """Test file operations."""
        print_section("Test 4: File Operations (Fixed)")
        
        try:
            from tools.file_tools import read_file, write_file
            
            # Test file writing
            test_content = "# Test Specification\n\nThis is a test file created by the AI team."
            test_file_path = "reports/test_lifecycle_fixed.md"
            
            write_result = write_file(
                file_path=test_file_path,
                content=test_content,
                agent_name="test_runner"
            )
            
            assert "successfully" in write_result.lower()
            print_success("File write operation successful")
            
            # Test file reading
            read_content = read_file(
                file_path=test_file_path,
                agent_name="test_runner"
            )
            
            assert read_content == test_content
            print_success("File read operation successful")
            
            # Cleanup
            test_file = PROJECT_ROOT / test_file_path
            if test_file.exists():
                test_file.unlink()
                print_info("Test file cleaned up")
                
            return True
                
        except Exception as e:
            print_error(f"File operations failed: {e}")
            return False

async def run_all_tests():
    """Run all fixed lifecycle tests."""
    print("🚀 Starting Fixed Lifecycle Test Suite...")
    
    test_suite = TestLifecycleFixed()
    results = {}
    
    try:
        # Test 1: Initialization
        with patch('workflows.agent_coordinator.create_agent_coordinator'):
            projektledare = test_suite.test_projektledare_initialization()
            results["initialization"] = projektledare is not None
        
        # Test 2: Feature Analysis
        with patch('workflows.agent_coordinator.create_agent_coordinator'):
            analysis = await test_suite.test_feature_analysis()
            results["feature_analysis"] = analysis is not None
        
        # Test 3: Story Breakdown
        with patch('workflows.agent_coordinator.create_agent_coordinator'):
            stories = await test_suite.test_story_breakdown()
            results["story_breakdown"] = stories is not None and len(stories) > 0
        
        # Test 4: File Operations
        with patch('workflows.agent_coordinator.create_agent_coordinator'):
            files_ok = test_suite.test_file_operations()
            results["file_operations"] = files_ok
        
        # Summary
        print_section("Test Results Summary")
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        print_info(f"Tests passed: {passed_tests}/{total_tests}")
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        if passed_tests == total_tests:
            print_success("🎉 All lifecycle tests passed!")
        else:
            print_error("🚨 Some tests failed - but we've identified the issue!")
        
        return results
        
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        return results

if __name__ == "__main__":
    # Run the fixed tests
    asyncio.run(run_all_tests())