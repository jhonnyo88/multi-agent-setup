#!/usr/bin/env python3
"""
Agent Coordination Integration Test Suite (Updated for Fast, Mocked Setup)
===========================================================================

PURPOSE:
This test suite validates the AgentCoordinator's logic without the overhead
of real agent initialization or execution. It uses extensive mocking to
ensure tests are fast, reliable, and focused.
"""

import sys
import asyncio
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from crewai import Agent, Task # Importera Agent för spec

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from workflows.agent_coordinator import AgentCoordinator, create_agent_coordinator, StoryWorkflow

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

TEST_STORIES = [
    {"story_id": "STORY-COORD-001", "title": "User Authentication", "description": "...", "story_type": "full_feature"},
    {"story_id": "STORY-COORD-002", "title": "API Rate Limiting", "description": "...", "story_type": "backend_only"},
]

def print_section(title: str): print(f"\n{'='*70}\n🧪 {title}\n{'='*70}")
def print_success(message: str): print(f"✅ {message}")
def print_info(message: str): print(f"ℹ️  {message}")

class TestAgentCoordination:

    @pytest.fixture
    def coordinator(self, mocker) -> AgentCoordinator:
        """
        Fixture som skapar en snabb AgentCoordinator genom att mocka de
        långsamma agent-skapande funktionerna.
        """
        # SLUTGILTIG KORRIGERING: Vi skapar en komplett och robust mock-agent
        # som har alla attribut som CrewAI validerar vid skapandet av en Task.
        mock_agent = MagicMock(spec=Agent)
        
        # Grundläggande attribut
        mock_agent.role = "Mocked Role"
        mock_agent.goal = "Mocked Goal"
        mock_agent.backstory = "Mocked Backstory"
        mock_agent.llm = MagicMock()
        mock_agent.tools = []

        # Konfigurations-attribut
        mock_agent.verbose = False
        mock_agent.memory = False
        mock_agent.cache = True
        mock_agent.allow_delegation = False
        mock_agent.max_iter = 15
        mock_agent.max_rpm = None
        mock_agent.step_callback = None
        
        # Interna/privata attribut som CrewAI kontrollerar
        mock_agent._rpm_controller = None
        mock_agent._token_process = None
        mock_agent.security_config = None # Den saknade attributen från senaste felet

        mocker.patch('workflows.agent_coordinator.create_speldesigner_agent', return_value=mock_agent)
        mocker.patch('workflows.agent_coordinator.create_utvecklare_agent', return_value=mock_agent)
        mocker.patch('workflows.agent_coordinator.create_testutvecklare_agent', return_value=mock_agent)
        mocker.patch('workflows.agent_coordinator.create_qa_testare_agent', return_value=mock_agent)
        mocker.patch('workflows.agent_coordinator.create_kvalitetsgranskare_agent', return_value=mock_agent)
        mocker.patch('workflows.agent_coordinator.create_projektledare', return_value=mock_agent)
        
        print_info("Creating fresh (and fast!) AgentCoordinator instance...")
        return create_agent_coordinator()

    async def test_coordinator_initialization(self, coordinator: AgentCoordinator):
        """Testar att koordinatorn kan skapas och konfigureras korrekt."""
        print_section("Test 1: Agent Coordinator Initialization")
        assert coordinator is not None
        assert hasattr(coordinator, 'agents')
        assert isinstance(coordinator.agents['speldesigner'], MagicMock)
        print_success("Agent coordinator initialized successfully.")

    async def test_story_delegation_and_task_creation(self, coordinator: AgentCoordinator):
        """Testar att en story kan delegeras och att korrekta tasks skapas."""
        print_section("Test 2: Story Delegation and Task Creation")
        test_story = TEST_STORIES[0]
        story_id = test_story["story_id"]
        coordinator._process_task_queue = AsyncMock()
        await coordinator.delegate_story(test_story)
        assert story_id in coordinator.active_stories
        workflow = coordinator.active_stories[story_id]
        expected_sequence = coordinator.workflow_sequences["full_feature"]
        assert len(workflow.tasks) == len(expected_sequence)
        print_success("Story delegated and tasks created correctly.")

    @patch('workflows.agent_coordinator.Crew.kickoff')
    async def test_full_workflow_execution_with_mocking(self, mock_kickoff, coordinator: AgentCoordinator):
        """End-to-end test av ett helt arbetsflöde med mockad agent-exekvering."""
        print_section("Test 3: Full Workflow Execution (Mocked)")
        test_story = TEST_STORIES[0]
        story_id = test_story["story_id"]
        expected_sequence = coordinator.workflow_sequences["full_feature"]
        mock_kickoff.side_effect = [f"Result from {agent_type}" for agent_type in expected_sequence]

        await coordinator.delegate_story(test_story)
        
        # Vänta på att arbetsflödet ska slutföras
        max_wait_time = 1
        for _ in range(int(max_wait_time / 0.05)):
            workflow = coordinator.active_stories.get(story_id)
            if workflow and workflow.overall_status == "completed":
                break
            await asyncio.sleep(0.05)
        
        workflow = coordinator.active_stories[story_id]
        assert workflow.overall_status == "completed", f"Workflow status was '{workflow.overall_status}', not 'completed'"
        assert mock_kickoff.call_count == len(expected_sequence)
        print_success("Full workflow simulated successfully.")

    async def test_status_and_monitoring_methods(self, coordinator: AgentCoordinator):
        """Testar get_story_status och get_team_status."""
        print_section("Test 4: Status and Team Monitoring")
        coordinator._execute_crewai_task = AsyncMock()
        for story_data in TEST_STORIES:
            await coordinator.delegate_story(story_data)
        
        team_status = coordinator.get_team_status()
        assert team_status["total_stories"] == len(TEST_STORIES)
        story_status = coordinator.get_story_status(TEST_STORIES[0]["story_id"])
        assert story_status is not None
        print_success("Status and monitoring methods are working correctly.")

    @patch('workflows.agent_coordinator.Crew.kickoff')
    async def test_exception_handling_in_execution(self, mock_kickoff, coordinator: AgentCoordinator):
        """
        Testar att ett fel under agent-exekvering hanteras korrekt.
        """
        print_section("Test 5: Exception Handling during Task Execution")

        error_message = "LLM API call failed"
        mock_kickoff.side_effect = Exception(error_message)
        
        test_story = TEST_STORIES[0]
        story_id = test_story["story_id"]

        print_info("Delegating a story that is expected to fail...")
        await coordinator.delegate_story(test_story)
        
        await asyncio.sleep(0.2)

        workflow = coordinator.active_stories[story_id]
        
        assert workflow.overall_status == "blocked", f"Expected status 'blocked', but got '{workflow.overall_status}'"
        assert workflow.tasks[0].status == "failed"
        assert error_message in (workflow.tasks[0].error_message or "")
        
        print_success("Exception during agent execution was handled gracefully.")
