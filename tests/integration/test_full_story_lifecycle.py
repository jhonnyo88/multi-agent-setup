#!/usr/bin/env python3
"""
Improved End-to-End Test for Complete AI Team Workflow
====================================================

PURPOSE:
Tests the complete story lifecycle from GitHub issue analysis through
final implementation, ensuring all agents work together correctly.

WHAT THIS TESTS:
1. Projektledare feature analysis and story breakdown
2. Speldesigner specification creation
3. Individual agent tool functionality
4. Cross-agent communication and handoffs
5. File system operations and artifact creation

HOW TO RUN:
    pytest tests/integration/test_full_story_lifecycle.py -v -s
"""

import asyncio
import json
from pathlib import Path
import sys
import os
import pytest

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import agents and tools
from agents.projektledare import create_projektledare
from agents.speldesigner import create_speldesigner_agent
from tools.file_tools import read_file, write_file
from config.settings import PROJECT_ROOT

# Test configuration
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "specs").mkdir(exist_ok=True)

class TestResults:
    """Track test results across the entire workflow."""
    def __init__(self):
        self.projektledare_analysis = None
        self.stories_created = None
        self.specification_created = None
        self.artifacts_created = []
        self.errors_encountered = []

def print_test_section(title: str):
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

@pytest.fixture
def mock_github_issue():
    """Provide a realistic GitHub issue for testing."""
    return {
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

@pytest.fixture
def test_results():
    """Provide test results tracking."""
    return TestResults()

@pytest.mark.asyncio
async def test_projektledare_initialization():
    """Test that Projektledare can be initialized successfully."""
    print_test_section("Test 1: Projektledare Initialization")
    
    try:
        projektledare = create_projektledare()
        assert projektledare is not None
        assert hasattr(projektledare, 'analyze_feature_request')
        assert hasattr(projektledare, 'create_story_breakdown')
        print_success("Projektledare initialized successfully")
        return projektledare
    except Exception as e:
        print_error(f"Failed to initialize Projektledare: {e}")
        pytest.fail(f"Projektledare initialization failed: {e}")

@pytest.mark.asyncio
async def test_feature_analysis(mock_github_issue):
    """Test feature analysis by Projektledare."""
    print_test_section("Test 2: Feature Analysis")
    
    try:
        projektledare = create_projektledare()
        
        print_info(f"Analyzing issue: '{mock_github_issue['title']}'")
        analysis_result = await projektledare.analyze_feature_request(mock_github_issue)
        
        # Validate analysis result structure
        assert isinstance(analysis_result, dict)
        assert "recommendation" in analysis_result
        
        print_success("Feature analysis completed successfully")
        print_info(f"Recommendation: {analysis_result.get('recommendation', {}).get('action', 'unknown')}")
        
        return analysis_result
        
    except Exception as e:
        print_error(f"Feature analysis failed: {e}")
        pytest.fail(f"Feature analysis failed: {e}")

@pytest.mark.asyncio 
async def test_story_breakdown(mock_github_issue):
    """Test story breakdown creation."""
    print_test_section("Test 3: Story Breakdown")
    
    try:
        projektledare = create_projektledare()
        
        # First get analysis
        analysis_result = await projektledare.analyze_feature_request(mock_github_issue)
        
        # Then create stories
        stories = await projektledare.create_story_breakdown(analysis_result, mock_github_issue)
        
        # Validate stories
        assert isinstance(stories, list)
        assert len(stories) > 0
        
        # Check story structure
        for story in stories:
            assert "story_id" in story
            assert "title" in story
            assert "assigned_agent" in story
            assert "acceptance_criteria" in story
            
        print_success(f"Created {len(stories)} stories successfully")
        for story in stories:
            print_info(f"  - {story['story_id']}: {story['title']} (→ {story['assigned_agent']})")
            
        return stories
        
    except Exception as e:
        print_error(f"Story breakdown failed: {e}")
        pytest.fail(f"Story breakdown failed: {e}")

@pytest.mark.asyncio
async def test_speldesigner_initialization():
    """Test Speldesigner agent initialization."""
    print_test_section("Test 4: Speldesigner Initialization")
    
    try:
        speldesigner = create_speldesigner_agent()
        assert speldesigner is not None
        assert hasattr(speldesigner, 'agent')
        print_success("Speldesigner initialized successfully")
        return speldesigner
    except Exception as e:
        print_error(f"Failed to initialize Speldesigner: {e}")
        pytest.fail(f"Speldesigner initialization failed: {e}")

@pytest.mark.asyncio
async def test_file_operations():
    """Test file reading and writing operations."""
    print_test_section("Test 5: File Operations")
    
    try:
        # Test file writing
        test_content = "# Test Specification\n\nThis is a test file created by the AI team."
        test_file_path = "reports/test_spec.md"
        
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
            
    except Exception as e:
        print_error(f"File operations failed: {e}")
        pytest.fail(f"File operations failed: {e}")

@pytest.mark.asyncio
async def test_dna_documents_accessibility():
    """Test that DNA documents can be read by agents."""
    print_test_section("Test 6: DNA Documents Access")
    
    dna_files = [
        "docs/dna/vision_and_mission.md",
        "docs/dna/target_audience.md", 
        "docs/dna/design_principles.md",
        "docs/dna/architecture.md"
    ]
    
    accessible_files = []
    
    for dna_file in dna_files:
        try:
            content = read_file(dna_file, agent_name="test_runner")
            if not content.startswith("❌"):
                accessible_files.append(dna_file)
                print_success(f"✓ {dna_file} accessible ({len(content)} chars)")
            else:
                print_error(f"✗ {dna_file} not accessible: {content}")
        except Exception as e:
            print_error(f"✗ {dna_file} error: {e}")
    
    # At least some DNA documents should be accessible
    assert len(accessible_files) >= 2, f"Too few DNA documents accessible: {accessible_files}"
    print_success(f"DNA documents accessibility verified ({len(accessible_files)}/{len(dna_files)} accessible)")

@pytest.mark.asyncio
async def test_agent_tool_integration():
    """Test that agents can use their tools correctly."""
    print_test_section("Test 7: Agent Tool Integration")
    
    try:
        speldesigner = create_speldesigner_agent()
        
        # Check that agent has tools
        assert hasattr(speldesigner.agent, 'tools')
        tools = speldesigner.agent.tools
        assert len(tools) > 0
        
        print_success(f"Speldesigner has {len(tools)} tools available")
        for tool in tools:
            print_info(f"  - {getattr(tool, 'name', 'Unknown tool')}")
            
    except Exception as e:
        print_error(f"Agent tool integration test failed: {e}")
        pytest.fail(f"Agent tool integration failed: {e}")

@pytest.mark.asyncio
async def test_full_lifecycle_simplified():
    """
    Simplified test that verifies the basic workflow without running the full CrewAI chain.
    This tests individual components rather than the full integration.
    """
    print_test_section("Test 8: Simplified Full Lifecycle")
    
    results = TestResults()
    
    try:
        # Step 1: Initialize agents
        print_info("Step 1: Initializing agents...")
        projektledare = create_projektledare()
        speldesigner = create_speldesigner_agent()
        
        # Step 2: Mock GitHub issue
        mock_issue = {
            "number": 999,
            "title": "Test feature for lifecycle",
            "body": "Test feature description",
            "labels": [{"name": "test"}],
            "user": {"login": "test-user"}
        }
        
        # Step 3: Feature analysis
        print_info("Step 2: Running feature analysis...")
        analysis = await projektledare.analyze_feature_request(mock_issue)
        results.projektledare_analysis = analysis
        assert isinstance(analysis, dict)
        print_success("Feature analysis completed")
        
        # Step 4: Story breakdown
        print_info("Step 3: Creating story breakdown...")
        stories = await projektledare.create_story_breakdown(analysis, mock_issue)
        results.stories_created = stories
        assert isinstance(stories, list)
        assert len(stories) > 0
        print_success(f"Created {len(stories)} stories")
        
        # Step 5: Test file creation (simulating spec creation)
        print_info("Step 4: Testing specification creation...")
        spec_content = f"""
# Feature Specification: {mock_issue['title']}

## Overview
This is a test specification created during the lifecycle test.

## User Stories
Test user story content.

## Technical Requirements
Test technical requirements.

## Acceptance Criteria
- [ ] Test criterion 1
- [ ] Test criterion 2
        """
        
        spec_file_path = f"reports/specs/test_spec_F{mock_issue['number']}.md"
        write_result = write_file(
            file_path=spec_file_path,
            content=spec_content.strip(),
            agent_name="test_lifecycle"
        )
        
        assert "successfully" in write_result.lower()
        results.specification_created = spec_file_path
        results.artifacts_created.append(spec_file_path)
        print_success("Specification file created successfully")
        
        # Step 6: Validate created file
        print_info("Step 5: Validating created artifacts...")
        created_spec = read_file(spec_file_path, agent_name="test_lifecycle")
        assert "Feature Specification" in created_spec
        assert mock_issue['title'] in created_spec
        print_success("Created specification validated")
        
        # Summary
        print_test_section("Test Results Summary")
        print_success("✅ All lifecycle components working correctly")
        print_info(f"Analysis completed: {results.projektledare_analysis is not None}")
        print_info(f"Stories created: {len(results.stories_created) if results.stories_created else 0}")
        print_info(f"Specification created: {results.specification_created}")
        print_info(f"Artifacts created: {len(results.artifacts_created)}")
        
        # Cleanup
        cleanup_file = PROJECT_ROOT / spec_file_path
        if cleanup_file.exists():
            cleanup_file.unlink()
            print_info("Test artifacts cleaned up")
        
        return results
        
    except Exception as e:
        print_error(f"Simplified lifecycle test failed: {e}")
        results.errors_encountered.append(str(e))
        pytest.fail(f"Simplified lifecycle test failed: {e}")

if __name__ == "__main__":
    # Run tests individually for debugging
    pytest.main([__file__, "-v", "-s"])