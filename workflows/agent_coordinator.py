"""
Agent Coordination System for DigiNativa AI Team
===============================================
(All din ursprungliga dokumentation är bevarad här)
"""

import asyncio
import logging
from collections import deque
from crewai import Crew, Task, Agent
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# --- Importer ---
from agents.speldesigner import create_speldesigner_agent
from agents.utvecklare import create_utvecklare_agent
from agents.testutvecklare import create_testutvecklare_agent
from agents.qa_testare import create_qa_testare_agent
from agents.kvalitetsgranskare import create_kvalitetsgranskare_agent
from agents.projektledare import create_projektledare

from workflows.status_handler import StatusHandler, report_error
from workflows.exception_handler import ExceptionHandler
from config.settings import AGENT_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Dataklasser ---
@dataclass
class StoryTask:
    task_id: str
    story_id: str
    agent_name: str
    task_type: str
    description: str
    dependencies: List[str]
    assigned_at: datetime
    status: str = "assigned"
    result_data: Optional[Dict[str, Any]] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class StoryWorkflow:
    story_id: str
    title: str
    description: str
    story_type: str
    created_at: datetime
    tasks: List[StoryTask] = field(default_factory=list)
    current_phase: str = "specification"
    overall_status: str = "active"
    completion_percentage: float = 0.0
    artifacts: List[str] = field(default_factory=list)

class AgentCoordinator:
    def __init__(self, status_handler: Optional[StatusHandler] = None):
        self.status_handler = status_handler
        self.exception_handler = ExceptionHandler(self.status_handler)
        self.active_stories: Dict[str, StoryWorkflow] = {}
        self.task_queue: deque[StoryTask] = deque()

        self.agents: Dict[str, Agent] = {
            "speldesigner": create_speldesigner_agent(),
            "utvecklare": create_utvecklare_agent(),
            "testutvecklare": create_testutvecklare_agent(),
            "qa_testare": create_qa_testare_agent(),
            "kvalitetsgranskare": create_kvalitetsgranskare_agent(),
            "projektledare": create_projektledare()
        }
        
        self.agent_capabilities = self._load_agent_capabilities()
        self.workflow_sequences = self._define_workflow_sequences()
        self.delegation_rules = self._define_delegation_rules()
        logger.info("AgentCoordinator initialiserad med %d agenter.", len(self.agents))

    def _load_agent_capabilities(self) -> Dict[str, Any]:
        return { "speldesigner": {}, "utvecklare": {}, "testutvecklare": {}, "qa_testare": {}, "kvalitetsgranskare": {} }

    def _define_workflow_sequences(self) -> Dict[str, List[str]]:
        return { "full_feature": ["specification", "backend", "frontend", "unit_testing", "integration_testing", "manual_testing", "quality_review"], "backend_only": ["specification", "backend", "unit_testing", "integration_testing", "quality_review"], "frontend_only": ["specification", "frontend", "unit_testing", "manual_testing", "quality_review"] }

    def _define_delegation_rules(self) -> Dict[str, str]:
        return { "specification": "speldesigner", "frontend": "utvecklare", "backend": "utvecklare", "unit_testing": "testutvecklare", "integration_testing": "testutvecklare", "manual_testing": "qa_testare", "quality_review": "kvalitetsgranskare" }

    async def delegate_story(self, story_data: Dict[str, Any]):
        story_id = story_data.get("story_id")
        if not story_id: raise ValueError("story_id is required.")
        
        workflow = self._create_story_workflow(story_data)
        self.active_stories[story_id] = workflow
        
        tasks = self._generate_story_tasks(story_data, workflow.story_type)
        workflow.tasks.extend(tasks)
        
        for task in tasks:
            if not task.dependencies:
                task.status = "queued"
                self.task_queue.append(task)

        asyncio.create_task(self._process_task_queue())

    def _create_story_workflow(self, story_data: Dict[str, Any]) -> StoryWorkflow:
        return StoryWorkflow(story_id=story_data["story_id"], title=story_data.get("title", "Untitled"), description=story_data.get("description", ""), story_type=story_data.get("story_type", "full_feature"), created_at=datetime.now())

    def _generate_story_tasks(self, story_data: Dict[str, Any], story_type: str) -> List[StoryTask]:
        tasks = []
        sequence = self.workflow_sequences.get(story_type, [])
        for i, task_type in enumerate(sequence):
            dependencies = [f"{story_data['story_id']}_{sequence[i-1]}"] if i > 0 else []
            tasks.append(StoryTask(task_id=f"{story_data['story_id']}_{task_type}", story_id=story_data['story_id'], agent_name=self.delegation_rules[task_type], task_type=task_type, description=f"{task_type} for {story_data['title']}", dependencies=dependencies, assigned_at=datetime.now()))
        return tasks

    async def _process_task_queue(self):
        tasks_to_requeue = []
        for _ in range(len(self.task_queue)):
            task = self.task_queue.popleft()
            if await self._can_start_task(task):
                task.status = "in_progress"
                asyncio.create_task(self._execute_crewai_task(task))
            else:
                tasks_to_requeue.append(task)
        if tasks_to_requeue:
            self.task_queue.extend(tasks_to_requeue)

    async def _can_start_task(self, task: StoryTask) -> bool:
        for dep_id in task.dependencies:
            dep_task = self._find_task_by_id(dep_id)
            if not dep_task or dep_task.status != "completed": return False
        return True

    async def _execute_crewai_task(self, task: StoryTask):
        try:
            agent_to_execute = self.agents[task.agent_name]
            crew_task = Task(description=task.description, agent=agent_to_execute, expected_output="A comprehensive result.")
            crew = Crew(agents=[agent_to_execute], tasks=[crew_task])
            result = await asyncio.get_running_loop().run_in_executor(None, crew.kickoff)
            task.result_data["output"] = result
            task.status = "completed"
            await self._handle_task_completion(task)
        except Exception as e:
            logger.exception(f"Error in task {task.task_id}")
            task.status = "failed"; task.error_message = str(e)
            await self._handle_task_failure(task)

    async def _handle_task_completion(self, completed_task: StoryTask):
        logger.info(f"Handling completion for task: {completed_task.task_id}")
        story = self.active_stories.get(completed_task.story_id)
        if not story: return

        for next_task in story.tasks:
            if completed_task.task_id in next_task.dependencies and next_task.status == "assigned":
                logger.info(f"Queuing next task: {next_task.task_id}")
                next_task.status = "queued"
                self.task_queue.append(next_task)
        
        self._update_story_progress(story)
        asyncio.create_task(self._process_task_queue())

    async def _handle_task_failure(self, task: StoryTask):
        story = self.active_stories.get(task.story_id)
        if story:
            story.overall_status = "blocked"

    def _update_story_progress(self, story: StoryWorkflow):
        completed_tasks = sum(1 for t in story.tasks if t.status == "completed")
        story.completion_percentage = (completed_tasks / len(story.tasks)) if story.tasks else 0
        if story.completion_percentage >= 1.0:
            story.overall_status = "completed"
            print(f"🎉 Story {story.story_id} completed successfully!")
        self._update_story_phase(story)

    def _update_story_phase(self, story: StoryWorkflow):
        # SLUTGILTIG KORRIGERING: Använder story.story_type istället för den
        # obefintliga variabeln story_data.
        completed_task_types = {t.task_type for t in story.tasks if t.status == "completed"}
        sequence = self.workflow_sequences.get(story.story_type, [])
        if not sequence: return

        last_completed_index = -1
        for i, task_type in enumerate(sequence):
            if task_type in completed_task_types:
                last_completed_index = i
        
        next_phase_index = last_completed_index + 1
        if next_phase_index < len(sequence):
            story.current_phase = sequence[next_phase_index]
        else:
            story.current_phase = "done"

    def _find_task_by_id(self, task_id: str) -> Optional[StoryTask]:
        for story in self.active_stories.values():
            for task in story.tasks:
                if task.task_id == task_id: return task
        return None

    def get_team_status(self) -> Dict[str, Any]:
        return {"total_stories": len(self.active_stories)}

def create_agent_coordinator() -> AgentCoordinator:
    return AgentCoordinator()
