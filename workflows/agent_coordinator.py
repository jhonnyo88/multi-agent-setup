"""
Agent Coordination System for DigiNativa AI Team
===============================================

PURPOSE:
Central coordination system that enables the Projektledare to delegate stories
to specialist agents and track their progress through the sequential workflow:
Specification → Code → Test → QA → Quality Review

WORKFLOW SEQUENCE:
1. Projektledare creates story breakdown
2. Stories are delegated to appropriate agents in correct order
3. Each agent reports status back to coordinator
4. Coordinator manages dependencies and handoffs
5. Progress is tracked until story completion

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update AGENT_CAPABILITIES for your team structure
2. Modify WORKFLOW_SEQUENCES for your development process
3. Adjust DELEGATION_RULES for your project requirements
4. Customize status handling for your quality gates
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from workflows.status_handler import StatusHandler, report_success, report_error
from workflows.exception_handler import ExceptionHandler
from config.settings import PROJECT_ROOT, AGENT_CONFIG

@dataclass
class StoryTask:
    """Represents a task assigned to an agent within a story."""
    task_id: str
    story_id: str
    agent_name: str
    task_type: str  # specification, frontend, backend, testing, qa, quality_review
    description: str
    dependencies: List[str]  # List of task_ids that must complete first
    assigned_at: datetime
    deadline: Optional[datetime] = None
    status: str = "assigned"  # assigned, in_progress, completed, failed, blocked
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@dataclass
class StoryWorkflow:
    """Tracks the complete workflow for a story."""
    story_id: str
    title: str
    description: str
    created_at: datetime
    tasks: List[StoryTask]
    current_phase: str  # specification, development, testing, qa, quality, done
    overall_status: str  # active, blocked, completed, failed
    completion_percentage: float = 0.0
    artifacts: List[str] = None  # File paths to created artifacts

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []

class AgentCoordinator:
    """
    Central coordination system for managing agent collaboration.
    
    RESPONSIBILITIES:
    - Delegate stories to appropriate agents based on capabilities
    - Track task dependencies and manage handoffs
    - Monitor progress and handle exceptions
    - Ensure sequential workflow compliance
    - Provide status updates to Projektledare
    
    DESIGN PRINCIPLES:
    - Agents are autonomous but coordinated
    - Clear dependencies prevent race conditions
    - Status tracking enables recovery and debugging
    - Exception handling prevents workflow stalls
    """
    
    def __init__(self):
        """Initialize coordinator with agent capabilities and workflow rules."""
        self.status_handler = StatusHandler()
        self.exception_handler = ExceptionHandler(self.status_handler)
        
        # Active stories being managed
        self.active_stories: Dict[str, StoryWorkflow] = {}
        
        # Task queue for pending work
        self.task_queue: List[StoryTask] = []
        
        # Agent capabilities mapping
        self.agent_capabilities = self._load_agent_capabilities()
        
        # Workflow sequence definitions
        self.workflow_sequences = self._define_workflow_sequences()
        
        # Delegation rules
        self.delegation_rules = self._define_delegation_rules()
        
        print("🎯 Agent Coordinator initialized")
        print(f"   Managing agents: {', '.join(self.agent_capabilities.keys())}")
        print(f"   Workflow sequences: {len(self.workflow_sequences)} defined")

    def _load_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Define what each agent can do and their specializations."""
        return {
            "speldesigner": {
                "capabilities": ["specification", "ux_design", "user_research"],
                "input_types": ["feature_analysis", "user_requirements"],
                "output_types": ["ux_specification", "design_mockups"],
                "max_concurrent_tasks": 2,
                "avg_completion_time_hours": 4,
                "quality_gates": ["design_principles_validation", "anna_persona_validation"]
            },
            "utvecklare": {
                "capabilities": ["frontend", "backend", "api_design", "database"],
                "input_types": ["ux_specification", "technical_requirements"],
                "output_types": ["react_components", "fastapi_endpoints", "database_schemas"],
                "max_concurrent_tasks": 1,  # Focused development
                "avg_completion_time_hours": 8,
                "quality_gates": ["architecture_compliance", "code_standards"]
            },
            "testutvecklare": {
                "capabilities": ["unit_testing", "integration_testing", "test_automation"],
                "input_types": ["code_files", "api_specifications"],
                "output_types": ["test_suites", "coverage_reports"],
                "max_concurrent_tasks": 3,
                "avg_completion_time_hours": 3,
                "quality_gates": ["test_coverage", "test_reliability"]
            },
            "qa_testare": {
                "capabilities": ["manual_testing", "usability_testing", "acceptance_testing"],
                "input_types": ["implemented_features", "user_scenarios"],
                "output_types": ["test_reports", "bug_reports", "approval_status"],
                "max_concurrent_tasks": 2,
                "avg_completion_time_hours": 4,
                "quality_gates": ["user_acceptance", "accessibility_compliance"]
            },
            "kvalitetsgranskare": {
                "capabilities": ["code_review", "performance_testing", "security_review"],
                "input_types": ["code_repositories", "deployed_applications"],
                "output_types": ["quality_reports", "performance_metrics"],
                "max_concurrent_tasks": 3,
                "avg_completion_time_hours": 2,
                "quality_gates": ["lighthouse_score", "security_scan"]
            }
        }

    def _define_workflow_sequences(self) -> Dict[str, List[str]]:
        """Define the sequential workflow for different story types."""
        return {
            "full_feature": [
                "specification",    # Speldesigner creates UX spec
                "backend",         # Utvecklare creates API
                "frontend",        # Utvecklare creates UI
                "unit_testing",    # Testutvecklare creates tests
                "integration_testing",  # Testutvecklare tests integration
                "manual_testing",  # QA-Testare validates from user perspective
                "quality_review"   # Kvalitetsgranskare final validation
            ],
            "backend_only": [
                "specification",
                "backend",
                "unit_testing",
                "integration_testing",
                "quality_review"
            ],
            "frontend_only": [
                "specification", 
                "frontend",
                "unit_testing",
                "manual_testing",
                "quality_review"
            ],
            "specification_only": [
                "specification"
            ]
        }

    def _define_delegation_rules(self) -> Dict[str, str]:
        """Map task types to responsible agents."""
        return {
            "specification": "speldesigner",
            "ux_design": "speldesigner",
            "frontend": "utvecklare", 
            "backend": "utvecklare",
            "api_design": "utvecklare",
            "unit_testing": "testutvecklare",
            "integration_testing": "testutvecklare",
            "test_automation": "testutvecklare",
            "manual_testing": "qa_testare",
            "usability_testing": "qa_testare",
            "acceptance_testing": "qa_testare",
            "quality_review": "kvalitetsgranskare",
            "performance_testing": "kvalitetsgranskare",
            "code_review": "kvalitetsgranskare"
        }

    async def delegate_story(self, story_data: Dict[str, Any]) -> str:
        """
        Delegate a story to appropriate agents based on story type and requirements.
        
        Args:
            story_data: Story information from Projektledare
            
        Returns:
            Story ID for tracking
        """
        try:
            story_id = story_data.get("story_id")
            story_type = story_data.get("story_type", "full_feature")
            
            print(f"📋 Delegating story {story_id} (type: {story_type})")
            
            # Create story workflow
            workflow = self._create_story_workflow(story_data)
            self.active_stories[story_id] = workflow
            
            # Generate tasks based on story type
            tasks = self._generate_story_tasks(story_data, story_type)
            workflow.tasks.extend(tasks)
            
            # Queue initial tasks (those with no dependencies)
            initial_tasks = [task for task in tasks if not task.dependencies]
            self.task_queue.extend(initial_tasks)
            
            # Update task statuses
            for task in initial_tasks:
                task.status = "queued"
                
            print(f"✅ Story {story_id} delegated with {len(tasks)} tasks")
            print(f"   Initial tasks: {[t.task_id for t in initial_tasks]}")
            
            # Start processing tasks
            await self._process_task_queue()
            
            return story_id
            
        except Exception as e:
            print(f"❌ Failed to delegate story: {e}")
            report_error("agent_coordinator", "DELEGATION_FAILED", str(e))
            raise

    def _create_story_workflow(self, story_data: Dict[str, Any]) -> StoryWorkflow:
        """Create workflow tracking object for story."""
        return StoryWorkflow(
            story_id=story_data.get("story_id"),
            title=story_data.get("title", ""),
            description=story_data.get("description", ""),
            created_at=datetime.now(),
            tasks=[],
            current_phase="specification",
            overall_status="active"
        )

    def _generate_story_tasks(self, story_data: Dict[str, Any], story_type: str) -> List[StoryTask]:
        """Generate the sequence of tasks for a story based on its type."""
        tasks = []
        story_id = story_data.get("story_id")
        
        # Get workflow sequence for story type
        sequence = self.workflow_sequences.get(story_type, self.workflow_sequences["full_feature"])
        
        for i, task_type in enumerate(sequence):
            # Determine dependencies (previous task in sequence)
            dependencies = []
            if i > 0:
                prev_task_id = f"{story_id}_{sequence[i-1]}"
                dependencies.append(prev_task_id)
            
            # Create task
            task = StoryTask(
                task_id=f"{story_id}_{task_type}",
                story_id=story_id,
                agent_name=self.delegation_rules.get(task_type, "unknown"),
                task_type=task_type,
                description=f"{task_type.replace('_', ' ').title()} for {story_data.get('title', story_id)}",
                dependencies=dependencies,
                assigned_at=datetime.now()
            )
            
            # Set deadline based on agent capabilities
            agent_caps = self.agent_capabilities.get(task.agent_name, {})
            avg_hours = agent_caps.get("avg_completion_time_hours", 4)
            task.deadline = datetime.now() + timedelta(hours=avg_hours)
            
            tasks.append(task)
        
        return tasks

    async def _process_task_queue(self):
        """Process queued tasks by delegating them to appropriate agents."""
        processed_tasks = []
        
        for task in self.task_queue:
            try:
                if await self._can_start_task(task):
                    success = await self._delegate_task_to_agent(task)
                    if success:
                        task.status = "in_progress"
                        processed_tasks.append(task)
                        print(f"✅ Task {task.task_id} delegated to {task.agent_name}")
                    else:
                        print(f"⚠️  Failed to delegate task {task.task_id}")
                        
            except Exception as e:
                print(f"❌ Error processing task {task.task_id}: {e}")
        
        # Remove processed tasks from queue
        for task in processed_tasks:
            self.task_queue.remove(task)

    async def _can_start_task(self, task: StoryTask) -> bool:
        """Check if a task can start based on dependencies and agent availability."""
        # Check dependencies are completed
        for dep_id in task.dependencies:
            dep_task = self._find_task_by_id(dep_id)
            if not dep_task or dep_task.status != "completed":
                return False
        
        # Check agent availability (basic implementation)
        agent_caps = self.agent_capabilities.get(task.agent_name, {})
        max_concurrent = agent_caps.get("max_concurrent_tasks", 1)
        
        # Count current tasks for this agent
        current_tasks = sum(1 for story in self.active_stories.values()
                           for t in story.tasks 
                           if t.agent_name == task.agent_name and t.status == "in_progress")
        
        return current_tasks < max_concurrent

    async def _delegate_task_to_agent(self, task: StoryTask) -> bool:
        """Delegate a specific task to an agent."""
        try:
            # Import agent classes dynamically to avoid circular imports
            if task.agent_name == "speldesigner":
                from agents.speldesigner import create_speldesigner_agent
                agent = create_speldesigner_agent()
                result = await self._execute_speldesigner_task(agent, task)
                
            elif task.agent_name == "utvecklare":
                from agents.utvecklare import create_utvecklare_agent
                agent = create_utvecklare_agent()
                result = await self._execute_utvecklare_task(agent, task)
                
            elif task.agent_name == "testutvecklare":
                from agents.testutvecklare import create_testutvecklare_agent
                agent = create_testutvecklare_agent()
                result = await self._execute_testutvecklare_task(agent, task)
                
            elif task.agent_name == "qa_testare":
                from agents.qa_testare import create_qa_testare_agent
                agent = create_qa_testare_agent()
                result = await self._execute_qa_task(agent, task)
                
            elif task.agent_name == "kvalitetsgranskare":
                from agents.kvalitetsgranskare import create_kvalitetsgranskare_agent
                agent = create_kvalitetsgranskare_agent()
                result = await self._execute_quality_task(agent, task)
                
            else:
                print(f"❌ Unknown agent: {task.agent_name}")
                return False
            
            # Store result and mark as completed
            if result:
                task.result_data = result
                task.status = "completed"
                await self._handle_task_completion(task)
                return True
            else:
                task.status = "failed"
                return False
                
        except Exception as e:
            print(f"❌ Task delegation failed: {e}")
            task.status = "failed"
            task.error_message = str(e)
            await self._handle_task_failure(task)
            return False

    async def _execute_speldesigner_task(self, agent, task: StoryTask) -> Optional[Dict[str, Any]]:
        """Execute a task with the Speldesigner agent."""
        story = self.active_stories[task.story_id]
        
        # Create mock feature analysis for Speldesigner
        feature_analysis = {
            "recommendation": {"action": "approve"},
            "complexity": {"estimated_stories": 1},
            "dna_alignment": {"design_principles_compatible": True}
        }
        
        # Create story details from task
        story_details = {
            "story_id": task.story_id,
            "title": story.title,
            "description": story.description,
            "user_value": f"Provides value for story {task.story_id}",
            "estimated_effort": "Medium"
        }
        
        # Execute specification creation
        result = await agent.create_ux_specification(feature_analysis, story_details)
        
        if result and not result.get("error"):
            # Add specification file to story artifacts
            if result.get("specification_file"):
                story.artifacts.append(result["specification_file"])
            return result
        
        return None

    async def _execute_utvecklare_task(self, agent, task: StoryTask) -> Optional[Dict[str, Any]]:
        """Execute a task with the Utvecklare agent."""
        # Find the specification from previous task
        story = self.active_stories[task.story_id]
        spec_file = None
        
        for artifact in story.artifacts:
            if "spec" in artifact.lower():
                spec_file = artifact
                break
        
        if not spec_file:
            print(f"⚠️  No specification found for development task {task.task_id}")
            return None
        
        # Execute implementation
        result = agent.implement_feature(spec_file, task.story_id)
        
        # For now, return a mock result as the agent implementation is complex
        return {
            "task_type": task.task_type,
            "completed": True,
            "artifacts": [f"frontend/src/components/{task.story_id}.tsx", 
                         f"backend/app/api/{task.story_id}.py"]
        }

    async def _execute_testutvecklare_task(self, agent, task: StoryTask) -> Optional[Dict[str, Any]]:
        """Execute a task with the Testutvecklare agent."""
        # Mock implementation for now
        return {
            "task_type": task.task_type,
            "completed": True,
            "test_coverage": 85,
            "tests_created": 12
        }

    async def _execute_qa_task(self, agent, task: StoryTask) -> Optional[Dict[str, Any]]:
        """Execute a task with the QA-Testare agent."""
        # Mock implementation for now
        return {
            "task_type": task.task_type,
            "completed": True,
            "approval_status": "approved",
            "usability_score": 4.2
        }

    async def _execute_quality_task(self, agent, task: StoryTask) -> Optional[Dict[str, Any]]:
        """Execute a task with the Kvalitetsgranskare agent."""
        # Mock implementation for now
        return {
            "task_type": task.task_type,
            "completed": True,
            "lighthouse_score": 92,
            "code_quality": 4.5
        }

    async def _handle_task_completion(self, task: StoryTask):
        """Handle successful task completion."""
        story = self.active_stories[task.story_id]
        
        # Update story progress
        completed_tasks = sum(1 for t in story.tasks if t.status == "completed")
        story.completion_percentage = completed_tasks / len(story.tasks)
        
        # Queue dependent tasks
        dependent_tasks = [t for t in story.tasks 
                          if task.task_id in t.dependencies and t.status == "assigned"]
        self.task_queue.extend(dependent_tasks)
        
        # Update story phase
        self._update_story_phase(story)
        
        # Check if story is complete
        if story.completion_percentage == 1.0:
            story.overall_status = "completed"
            story.current_phase = "done"
            print(f"🎉 Story {story.story_id} completed successfully!")
        
        # Process newly queued tasks
        await self._process_task_queue()

    async def _handle_task_failure(self, task: StoryTask):
        """Handle task failure and trigger exception handling."""
        story = self.active_stories[task.story_id]
        story.overall_status = "blocked"
        
        # Trigger exception handling
        resolution = await self.exception_handler.handle_exception(
            "TASK_EXECUTION_FAILED",
            {
                "task_id": task.task_id,
                "agent_name": task.agent_name,
                "error_message": task.error_message
            },
            task.story_id
        )
        
        if resolution.handled:
            print(f"🔧 Task failure handled: {task.task_id}")
            # Reset task for retry if appropriate
            if resolution.retry_recommended:
                task.status = "assigned"
                self.task_queue.append(task)
        else:
            print(f"🚨 Task failure requires human intervention: {task.task_id}")

    def _update_story_phase(self, story: StoryWorkflow):
        """Update story phase based on completed tasks."""
        completed_task_types = {t.task_type for t in story.tasks if t.status == "completed"}
        
        if "quality_review" in completed_task_types:
            story.current_phase = "done"
        elif "manual_testing" in completed_task_types:
            story.current_phase = "quality"
        elif any(t in completed_task_types for t in ["unit_testing", "integration_testing"]):
            story.current_phase = "qa"
        elif any(t in completed_task_types for t in ["frontend", "backend"]):
            story.current_phase = "testing"
        elif "specification" in completed_task_types:
            story.current_phase = "development"

    def _find_task_by_id(self, task_id: str) -> Optional[StoryTask]:
        """Find a task by its ID across all active stories."""
        for story in self.active_stories.values():
            for task in story.tasks:
                if task.task_id == task_id:
                    return task
        return None

    def get_story_status(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status information for a story."""
        story = self.active_stories.get(story_id)
        if not story:
            return None
        
        return {
            "story_id": story.story_id,
            "title": story.title,
            "overall_status": story.overall_status,
            "current_phase": story.current_phase,
            "completion_percentage": story.completion_percentage,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "agent_name": task.agent_name,
                    "task_type": task.task_type,
                    "status": task.status,
                    "assigned_at": task.assigned_at.isoformat(),
                    "deadline": task.deadline.isoformat() if task.deadline else None
                }
                for task in story.tasks
            ],
            "artifacts": story.artifacts
        }

    def get_team_status(self) -> Dict[str, Any]:
        """Get overall team status across all active stories."""
        active_count = len([s for s in self.active_stories.values() if s.overall_status == "active"])
        completed_count = len([s for s in self.active_stories.values() if s.overall_status == "completed"])
        blocked_count = len([s for s in self.active_stories.values() if s.overall_status == "blocked"])
        
        # Agent workload
        agent_workload = {}
        for agent in self.agent_capabilities.keys():
            active_tasks = sum(1 for story in self.active_stories.values()
                             for task in story.tasks
                             if task.agent_name == agent and task.status == "in_progress")
            agent_workload[agent] = active_tasks
        
        return {
            "active_stories": active_count,
            "completed_stories": completed_count,
            "blocked_stories": blocked_count,
            "queued_tasks": len(self.task_queue),
            "agent_workload": agent_workload,
            "total_stories": len(self.active_stories)
        }

# Factory function for easy instantiation
def create_agent_coordinator() -> AgentCoordinator:
    """Create and initialize the agent coordination system."""
    return AgentCoordinator()