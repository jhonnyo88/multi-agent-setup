"""
Agent Chain Coordinator för DigiNativa
======================================

PURPOSE:
Orchestrates the agent chain according to target workflow:
Speldesigner → Backend → Frontend → Test → QA → Quality → Review

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Line 45-60: Update AgentType enum for your agents
2. Line 85-150: Modify agent chain structure for your workflow
3. Line 200-250: Adapt task execution logic for your tools
4. Line 300-350: Update deliverables per agent type

CONFIGURATION POINTS:
- Line 45: Agent types definition
- Line 150: Task dependency chain
- Line 280: Quality gates per agent
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime, timedelta

class AgentType(Enum):
    """Available agent types in the DigiNativa team"""
    SPELDESIGNER = "speldesigner"
    UTVECKLARE_BACKEND = "utvecklare_backend"
    UTVECKLARE_FRONTEND = "utvecklare_frontend"
    TESTUTVECKLARE = "testutvecklare"
    QA_TESTARE = "qa_testare"
    KVALITETSGRANSKARE = "kvalitetsgranskare"

class TaskStatus(Enum):
    """Status values for agent tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class AgentTask:
    """
    A task assigned to a specific agent in the chain.
    
    Represents one step in the feature development process,
    with clear prerequisites, deliverables, and quality gates.
    """
    agent_type: AgentType
    issue_number: int
    story_id: str
    description: str
    prerequisites: List[str]  # Task IDs that must complete before this task
    deliverables: List[str]   # What the agent must deliver
    estimated_hours: int
    quality_gates: List[str] = field(default_factory=list)  # Quality checks to pass
    status: TaskStatus = TaskStatus.PENDING
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class ChainResult:
    """Result of executing an agent chain"""
    issue_number: int
    overall_status: str  # completed, failed, in_progress, blocked
    completed_tasks: List[str]
    failed_tasks: List[str]
    total_execution_time: Optional[timedelta] = None
    deliverables: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None

class AgentChainCoordinator:
    """
    Coordinates the agent chain for feature development.
    
    HAPPY FLOW IMPLEMENTATION:
    1. Feature breakdown → Stories
    2. Speldesigner → UX Specification
    3. Backend Dev → API Implementation
    4. Frontend Dev → UI Implementation  
    5. Test Dev → Automated Tests
    6. QA Tester → Manual Testing
    7. Quality → Performance & Code Review
    8. Project Owner → Final Approval
    
    DEPENDENCY MANAGEMENT:
    - Each task specifies prerequisites
    - Tasks execute only when prerequisites complete
    - Failed tasks block dependent tasks
    - Retry logic for recoverable failures
    """
    
    def __init__(self, agents_registry: Dict[AgentType, Any]):
        """
        Initialize coordinator with agent registry.
        
        Args:
            agents_registry: Dictionary mapping AgentType to agent instances
        """
        self.agents = agents_registry
        self.active_chains: Dict[int, List[AgentTask]] = {}  # issue_number -> task chain
        self.chain_results: Dict[int, ChainResult] = {}
        
    def create_agent_chain_for_feature(self, issue_number: int, feature_analysis: Dict) -> List[AgentTask]:
        """
        Create agent chain based on feature analysis.
        
        DEPENDENCY CHAIN STRUCTURE:
        Speldesigner (no prereq) → 
        Backend (needs UX spec) → 
        Frontend (needs UX spec + API) →
        Test (needs code) →
        QA (needs everything) →
        Quality (needs everything)
        
        Args:
            issue_number: GitHub issue number
            feature_analysis: Analysis results from projektledare
            
        Returns:
            List of AgentTask objects in dependency order
        """
        complexity = feature_analysis.get('complexity', {})
        estimated_stories = complexity.get('estimated_stories', 1)
        
        tasks = []
        
        # Task 1: UX Specification (Speldesigner)
        # No prerequisites - can start immediately
        tasks.append(AgentTask(
            agent_type=AgentType.SPELDESIGNER,
            issue_number=issue_number,
            story_id=f"{issue_number}-ux-spec",
            description="Create UX specification according to 5 design principles",
            prerequisites=[],  # No prerequisites - first in chain
            deliverables=[
                "UX wireframes and mockups",
                "User journey maps", 
                "Component specifications",
                "Design system guidelines",
                "Accessibility requirements"
            ],
            estimated_hours=complexity.get('ux_hours', 8),
            quality_gates=[
                "Design principles compliance check",
                "Target audience (Anna) validation",
                "Mobile responsiveness verification"
            ]
        ))
        
        # Task 2: Backend Implementation (Utvecklare Backend)
        # Requires UX spec to understand API requirements
        tasks.append(AgentTask(
            agent_type=AgentType.UTVECKLARE_BACKEND,
            issue_number=issue_number,
            story_id=f"{issue_number}-backend",
            description="Implement FastAPI backend according to architecture",
            prerequisites=[f"{issue_number}-ux-spec"],
            deliverables=[
                "FastAPI endpoints implementation",
                "Pydantic data models",
                "Business logic services",
                "Database migrations (if needed)",
                "OpenAPI documentation",
                "Error handling and validation"
            ],
            estimated_hours=complexity.get('backend_hours', 16),
            quality_gates=[
                "API-first architecture compliance",
                "Stateless backend verification", 
                "Error handling completeness",
                "OpenAPI documentation accuracy"
            ]
        ))
        
        # Task 3: Frontend Implementation (Utvecklare Frontend)
        # Requires both UX spec and backend API
        tasks.append(AgentTask(
            agent_type=AgentType.UTVECKLARE_FRONTEND,
            issue_number=issue_number,
            story_id=f"{issue_number}-frontend",
            description="Implement React frontend according to UX specification",
            prerequisites=[f"{issue_number}-ux-spec", f"{issue_number}-backend"],
            deliverables=[
                "React components implementation",
                "State management setup",
                "API integration with backend",
                "Responsive design implementation",
                "Accessibility compliance",
                "Tailwind CSS styling"
            ],
            estimated_hours=complexity.get('frontend_hours', 12),
            quality_gates=[
                "Component reusability check",
                "API integration verification",
                "Responsive design validation",
                "Accessibility audit"
            ]
        ))
        
        # Task 4: Test Development (Testutvecklare)
        # Requires both backend and frontend to exist
        tasks.append(AgentTask(
            agent_type=AgentType.TESTUTVECKLARE,
            issue_number=issue_number,
            story_id=f"{issue_number}-tests",
            description="Create comprehensive automated tests for all components",
            prerequisites=[f"{issue_number}-backend", f"{issue_number}-frontend"],
            deliverables=[
                "Backend unit tests (pytest)",
                "Frontend component tests (Jest/RTL)",
                "API integration tests",
                "End-to-end tests (Playwright)",
                "Test coverage reports",
                "Test documentation"
            ],
            estimated_hours=complexity.get('test_hours', 8),
            quality_gates=[
                "Minimum 80% code coverage",
                "All API endpoints tested",
                "Critical user paths covered",
                "Test reliability verification"
            ]
        ))
        
        # Task 5: QA Testing (QA Testare)
        # Requires all implementation and tests to be ready
        tasks.append(AgentTask(
            agent_type=AgentType.QA_TESTARE,
            issue_number=issue_number,
            story_id=f"{issue_number}-qa",
            description="Manual testing from Anna persona perspective",
            prerequisites=[f"{issue_number}-tests"],
            deliverables=[
                "Manual test execution results",
                "User acceptance validation",
                "Design principles compliance verification",
                "Cross-browser compatibility check",
                "Mobile device testing results",
                "Bug reports and recommendations"
            ],
            estimated_hours=complexity.get('qa_hours', 6),
            quality_gates=[
                "All 5 design principles satisfied",
                "Anna persona journey validated",
                "Zero critical bugs",
                "Performance acceptable"
            ]
        ))
        
        # Task 6: Quality Review (Kvalitetsgranskare)
        # Final quality gate before project owner review
        tasks.append(AgentTask(
            agent_type=AgentType.KVALITETSGRANSKARE,
            issue_number=issue_number,
            story_id=f"{issue_number}-quality",
            description="Performance and code quality final review",
            prerequisites=[f"{issue_number}-qa"],
            deliverables=[
                "Lighthouse performance audit",
                "Code quality metrics report",
                "Security scan results",
                "Performance optimization recommendations",
                "Architecture compliance verification",
                "Production readiness assessment"
            ],
            estimated_hours=complexity.get('quality_hours', 4),
            quality_gates=[
                "Lighthouse score >90",
                "No critical security issues",
                "Code quality standards met",
                "Performance benchmarks achieved"
            ]
        ))
        
        # Store chain for tracking
        self.active_chains[issue_number] = tasks
        
        print(f"🏁 Chain execution completed for #{issue_number}")
        print(f"   Status: {result.overall_status}")
        print(f"   Completed: {len(result.completed_tasks)}/{len(chain)} tasks")
        print(f"   Duration: {result.total_execution_time}")
        
        return result
    
    def get_chain_status(self, issue_number: int) -> Dict[str, Any]:
        """
        Get current status of an agent chain.
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            Dictionary with chain status and progress details
        """
        if issue_number not in self.active_chains:
            return {"error": "Chain not found", "issue_number": issue_number}
        
        chain = self.active_chains[issue_number]
        
        status = {
            "issue_number": issue_number,
            "total_tasks": len(chain),
            "completed_tasks": len([t for t in chain if t.status == TaskStatus.COMPLETED]),
            "in_progress_tasks": len([t for t in chain if t.status == TaskStatus.IN_PROGRESS]),
            "pending_tasks": len([t for t in chain if t.status == TaskStatus.PENDING]),
            "failed_tasks": len([t for t in chain if t.status == TaskStatus.FAILED]),
            "progress_percentage": 0,
            "estimated_total_hours": sum(task.estimated_hours for task in chain),
            "task_details": []
        }
        
        # Calculate progress percentage
        if status["total_tasks"] > 0:
            status["progress_percentage"] = (status["completed_tasks"] / status["total_tasks"]) * 100
        
        # Add detailed task information
        for task in chain:
            task_detail = {
                "story_id": task.story_id,
                "agent": task.agent_type.value,
                "status": task.status.value,
                "estimated_hours": task.estimated_hours,
                "description": task.description,
                "prerequisites": task.prerequisites,
                "deliverables": task.deliverables,
                "quality_gates": task.quality_gates
            }
            
            # Add timing information if available
            if task.assigned_at:
                task_detail["assigned_at"] = task.assigned_at.isoformat()
            if task.completed_at:
                task_detail["completed_at"] = task.completed_at.isoformat()
                task_detail["duration"] = str(task.completed_at - task.assigned_at)
            
            # Add error information if failed
            if task.status == TaskStatus.FAILED and task.error_message:
                task_detail["error_message"] = task.error_message
            
            status["task_details"].append(task_detail)
        
        return status
    
    def print_chain_summary(self, issue_number: int):
        """Print human-readable summary of chain status."""
        status = self.get_chain_status(issue_number)
        
        if "error" in status:
            print(f"❌ {status['error']} for issue #{issue_number}")
            return
        
        print(f"\n📊 AGENT CHAIN STATUS - Issue #{issue_number}")
        print("=" * 60)
        print(f"Progress: {status['completed_tasks']}/{status['total_tasks']} tasks ({status['progress_percentage']:.1f}%)")
        print(f"Estimated total: {status['estimated_total_hours']} hours")
        
        print(f"\n📋 Task Breakdown:")
        for task in status['task_details']:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'failed': '❌',
                'blocked': '🔴'
            }.get(task['status'], '⚪')
            
            prereq_str = f" (after: {', '.join(task['prerequisites'])})" if task['prerequisites'] else ""
            print(f"  {status_emoji} {task['agent']}: {task['description'][:50]}...{prereq_str}")
            
            if task['status'] == 'failed' and 'error_message' in task:
                print(f"      ❌ Error: {task['error_message']}")
    
    def get_all_chains_summary(self) -> Dict[str, Any]:
        """Get summary of all active chains."""
        summary = {
            "total_chains": len(self.active_chains),
            "completed_chains": 0,
            "in_progress_chains": 0,
            "failed_chains": 0,
            "chains": []
        }
        
        for issue_number in self.active_chains:
            chain_status = self.get_chain_status(issue_number)
            
            # Determine overall chain status
            if chain_status["failed_tasks"] > 0:
                overall_status = "failed"
                summary["failed_chains"] += 1
            elif chain_status["completed_tasks"] == chain_status["total_tasks"]:
                overall_status = "completed"
                summary["completed_chains"] += 1
            else:
                overall_status = "in_progress"
                summary["in_progress_chains"] += 1
            
            summary["chains"].append({
                "issue_number": issue_number,
                "status": overall_status,
                "progress": f"{chain_status['completed_tasks']}/{chain_status['total_tasks']}",
                "progress_percentage": chain_status["progress_percentage"]
            })
        
        return summary
    
    async def retry_failed_task(self, issue_number: int, story_id: str) -> bool:
        """
        Retry a failed task in the chain.
        
        Args:
            issue_number: GitHub issue number
            story_id: Task story ID to retry
            
        Returns:
            True if retry successful, False otherwise
        """
        if issue_number not in self.active_chains:
            print(f"❌ No chain found for issue #{issue_number}")
            return False
        
        chain = self.active_chains[issue_number]
        task_to_retry = None
        
        for task in chain:
            if task.story_id == story_id:
                task_to_retry = task
                break
        
        if not task_to_retry:
            print(f"❌ Task {story_id} not found in chain")
            return False
        
        if task_to_retry.status != TaskStatus.FAILED:
            print(f"❌ Task {story_id} is not in failed status")
            return False
        
        print(f"🔄 Retrying task: {story_id}")
        
        try:
            # Reset task status
            task_to_retry.status = TaskStatus.PENDING
            task_to_retry.error_message = None
            task_to_retry.assigned_at = None
            task_to_retry.completed_at = None
            
            # Re-execute just this task (simplified version)
            task_to_retry.status = TaskStatus.IN_PROGRESS
            task_to_retry.assigned_at = datetime.now()
            
            agent = self.agents.get(task_to_retry.agent_type)
            if not agent:
                raise Exception(f"Agent {task_to_retry.agent_type.value} not found")
            
            task_result = await agent.execute_task(task_to_retry)
            
            if task_result.get("success"):
                task_to_retry.status = TaskStatus.COMPLETED
                task_to_retry.completed_at = datetime.now()
                task_to_retry.result_data = task_result.get("data", {})
                print(f"✅ Retry successful: {story_id}")
                return True
            else:
                task_to_retry.status = TaskStatus.FAILED
                task_to_retry.error_message = task_result.get("error", "Retry failed")
                print(f"❌ Retry failed: {story_id}")
                return False
                
        except Exception as e:
            task_to_retry.status = TaskStatus.FAILED
            task_to_retry.error_message = str(e)
            print(f"❌ Retry exception: {story_id} - {str(e)}")
            return Falsef"✅ Created agent chain for #{issue_number} with {len(tasks)} tasks")
        for task in tasks:
            prereq_str = f" (after: {', '.join(task.prerequisites)})" if task.prerequisites else " (no prereqs)"
            print(f"   {task.agent_type.value}: {task.estimated_hours}h{prereq_str}")
        
        return tasks
    
    async def execute_agent_chain(self, issue_number: int) -> ChainResult:
        """
        Execute the agent chain for a feature.
        
        EXECUTION LOGIC:
        1. Check prerequisites for each task
        2. Run tasks in dependency order when prerequisites are satisfied
        3. Handle errors and retry logic
        4. Collect deliverables and results
        5. Return comprehensive result to projektledare
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            ChainResult with execution summary and deliverables
        """
        if issue_number not in self.active_chains:
            return ChainResult(
                issue_number=issue_number,
                overall_status="failed",
                completed_tasks=[],
                failed_tasks=[],
                error_details="No agent chain found for issue"
            )
        
        start_time = datetime.now()
        chain = self.active_chains[issue_number]
        
        result = ChainResult(
            issue_number=issue_number,
            overall_status="in_progress",
            completed_tasks=[],
            failed_tasks=[]
        )
        
        # Track completed tasks by story_id
        completed_tasks = set()
        
        print(f"🚀 Starting agent chain execution for #{issue_number}")
        
        # Main execution loop
        while len(completed_tasks) < len(chain):
            # Find next runnable task
            next_task = None
            for task in chain:
                if (task.story_id not in completed_tasks and 
                    task.status == TaskStatus.PENDING and
                    all(prereq in completed_tasks for prereq in task.prerequisites)):
                    next_task = task
                    break
            
            if not next_task:
                # Check if we're done or deadlocked
                if len(completed_tasks) == len(chain):
                    result.overall_status = "completed"
                    break
                else:
                    # Deadlock - no runnable tasks
                    result.overall_status = "deadlock"
                    result.error_details = "No runnable tasks found - possible circular dependencies"
                    break
            
            # Execute the task
            try:
                print(f"   🎯 Executing: {next_task.agent_type.value} - {next_task.description}")
                
                next_task.status = TaskStatus.IN_PROGRESS
                next_task.assigned_at = datetime.now()
                
                # Get agent and execute task
                agent = self.agents.get(next_task.agent_type)
                if not agent:
                    raise Exception(f"Agent {next_task.agent_type.value} not found in registry")
                
                # Execute agent task (this will be implemented by each agent)
                task_result = await agent.execute_task(next_task)
                
                if task_result.get("success"):
                    next_task.status = TaskStatus.COMPLETED
                    next_task.completed_at = datetime.now()
                    next_task.result_data = task_result.get("data", {})
                    
                    completed_tasks.add(next_task.story_id)
                    result.completed_tasks.append(next_task.story_id)
                    result.deliverables[next_task.story_id] = task_result.get("deliverables", {})
                    
                    print(f"   ✅ Completed: {next_task.agent_type.value}")
                else:
                    # Task failed
                    next_task.status = TaskStatus.FAILED
                    next_task.error_message = task_result.get("error", "Unknown error")
                    result.failed_tasks.append(next_task.story_id)
                    result.overall_status = "failed"
                    result.error_details = f"Task {next_task.story_id} failed: {next_task.error_message}"
                    break
                    
            except Exception as e:
                next_task.status = TaskStatus.FAILED
                next_task.error_message = str(e)
                result.failed_tasks.append(next_task.story_id)
                result.overall_status = "failed"
                result.error_details = f"Exception in task {next_task.story_id}: {str(e)}"
                print(f"   ❌ Failed: {next_task.agent_type.value} - {str(e)}")
                break
        
        # Calculate total execution time
        end_time = datetime.now()
        result.total_execution_time = end_time - start_time
        
        # Store result for future reference
        self.chain_results[issue_number] = result
        
        print(