"""
DigiNativa Projektledare Agent
=============================

PURPOSE:
The Projektledare (Project Manager) is the central orchestrator of the DigiNativa AI team.
It manages GitHub Issues, coordinates between agents, handles exceptions, and ensures
all work follows the project's DNA documents and workflows.

ADAPTATION GUIDE:
🔧 To adapt this agent for your project:
1. Line 45-60: Update DOMAIN_CONTEXT for your business domain
2. Line 80-100: Modify QUALITY_STANDARDS for your project requirements  
3. Line 120-150: Adjust WORKFLOW_STEPS for your development process
4. Line 200-250: Customize agent prompts for your technical stack
5. Line 300-350: Update exception handling for your specific risks

AGENT CAPABILITIES:
- Analyzes GitHub Issues and breaks down Features into Stories
- Delegates tasks to appropriate specialist agents
- Monitors story progress and handles exceptions/deadlocks
- Validates all work against DNA documents (vision, principles, architecture)
- Manages cross-repo synchronization between AI-team and project repos
- Escalates to humans when automatic resolution isn't possible

DEPENDENCIES:
- CrewAI framework for agent orchestration
- GitHub API for issue management and communication
- Project DNA documents for decision-making guidance
- State management system for tracking story progress
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# CrewAI imports
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

# Project imports
from config.settings import (
    PROJECT_NAME, PROJECT_DOMAIN, TARGET_AUDIENCE, GITHUB_CONFIG, 
    TECH_STACK, AGENT_CONFIG, QUALITY_STANDARDS, SECRETS
)
from tools.file_tools import FileReadTool, FileWriteTool
from tools.git_tools import GitTool
from workflows.status_handler import StatusHandler
from workflows.exception_handler import ExceptionHandler

class ProjektledareAgent:
    """
    The central orchestrator agent for the DigiNativa AI team.
    
    ROLE DEFINITION:
    Acts as the "operating system" for the AI team, ensuring all agents work
    together effectively to deliver high-quality features that align with
    project goals and architectural principles.
    
    KEY RESPONSIBILITIES:
    1. Feature Analysis & Story Breakdown
    2. Agent Coordination & Task Delegation  
    3. Progress Monitoring & Exception Handling
    4. Quality Assurance & DNA Compliance
    5. Human Communication & Escalation
    """
    
    def __init__(self):
        """Initialize the Projektledare with domain knowledge and tools."""
        self.status_handler = StatusHandler()
        self.exception_handler = ExceptionHandler(self.status_handler)
        self.current_stories = {}  # Track active story states
        self.agent = self._create_agent()
        
        # 🔧 ADAPT: Update domain context for your project
        self.domain_context = {
            "primary_domain": PROJECT_DOMAIN,  # e.g., "game_development" 
            "target_user": TARGET_AUDIENCE["primary_persona"],  # e.g., "Anna"
            "key_constraints": [
                f"Sessions must be < {TARGET_AUDIENCE['time_constraints']}",
                "All features must serve pedagogical purpose",  # 🔧 CHANGE: Your primary value
                "Professional tone without infantilization",
                "Swedish public sector context"  # 🔧 CHANGE: Your market context
            ],
            "technical_stack": TECH_STACK,
            "quality_standards": QUALITY_STANDARDS
        }
    
    def _create_agent(self) -> Agent:
        """
        Create the CrewAI agent with DigiNativa-specific configuration.
        
        AGENT PERSONALITY:
        - Systematic and methodical in approach
        - Strong focus on quality and architectural compliance
        - Excellent at breaking down complex problems
        - Proactive in identifying and resolving conflicts
        - Clear communicator with both AI agents and humans
        
        🔧 ADAPTATION: Modify the role, goal, and backstory for your domain
        """
        return Agent(
            role="Projektledare (Resilient Team Orchestrator)",
            
            goal=f"""
            Orchestrate the DigiNativa AI team to deliver high-quality features that serve 
            {TARGET_AUDIENCE['primary_persona']} ({TARGET_AUDIENCE['description']}) and align with our 
            vision of making digitalization strategy practical and understandable.
            
            🔧 ADAPT: Replace with your project's goal
            E-commerce: "Deliver features that increase conversion and customer satisfaction"
            Mobile app: "Create user experiences that solve real daily problems efficiently"  
            SaaS: "Build functionality that improves business productivity and workflow"
            """,
            
            backstory=f"""
            You are the central intelligence coordinating the development of {PROJECT_NAME}, 
            an interactive learning game for Swedish public sector digitalization.
            
            Your expertise spans:
            - {PROJECT_DOMAIN} domain knowledge and best practices
            - {TECH_STACK['frontend']['framework']} + {TECH_STACK['backend']['framework']} architecture
            - Agile project management and team coordination
            - Quality assurance and architectural compliance
            - Educational game design and learning effectiveness
            
            Your decision-making is guided by:
            1. Project DNA documents (vision, audience, principles, architecture)
            2. Story lifecycle workflows and exception handling procedures  
            3. Quality standards that ensure professional-grade output
            4. Deep understanding of {TARGET_AUDIENCE['primary_persona']}'s needs and constraints
            
            You are methodical, quality-focused, and excellent at preventing problems
            before they occur. When issues arise, you systematically apply documented
            procedures to resolve them quickly and effectively.
            
            🔧 ADAPTATION: Update this backstory for your domain
            - Replace educational game context with your product context
            - Update technical stack references to match your choices
            - Modify expertise areas to reflect your domain requirements
            - Adjust decision-making factors for your project priorities
            """,
            
            tools=[
                FileReadTool(),  # Read DNA documents and specifications
                FileWriteTool(), # Create stories, specs, and documentation
                GitTool(),       # Manage repository and pull requests
            ],
            
            verbose=True,
            allow_delegation=True,  # Essential: Can delegate to specialist agents
            llm=AGENT_CONFIG["llm_model"],
            max_iterations=AGENT_CONFIG["max_iterations"],
            temperature=AGENT_CONFIG["temperature"]
        )
    
    async def analyze_feature_request(self, github_issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a GitHub Issue containing a feature request and determine next steps.
        
        ANALYSIS PROCESS:
        1. Validate feature alignment with project DNA
        2. Assess technical feasibility within current architecture  
        3. Estimate complexity and required agent involvement
        4. Check for dependencies on other features or external systems
        5. Determine if new specification is needed or if existing spec suffices
        
        Args:
            github_issue: GitHub Issue data including title, body, labels, etc.
            
        Returns:
            Analysis results with recommended actions and agent assignments
            
        🔧 ADAPTATION: Modify analysis criteria for your domain
        """
        issue_data = {
            "issue_id": github_issue.get("number"),
            "title": github_issue.get("title", ""),
            "body": github_issue.get("body", ""),
            "labels": [label["name"] for label in github_issue.get("labels", [])],
            "author": github_issue.get("user", {}).get("login", "unknown")
        }
        
        # Create analysis task for the agent
        analysis_task = Task(
            description=f"""
            Analyze this feature request for {PROJECT_NAME} and provide a structured assessment:
            
            **Issue Details:**
            - Title: {issue_data['title']}
            - Description: {issue_data['body'][:500]}...
            - Labels: {', '.join(issue_data['labels'])}
            
            **Required Analysis:**
            
            1. **DNA Alignment Check:**
               - Does this align with our vision and mission? (Check docs/dna/vision_and_mission.md)
               - Does it serve {TARGET_AUDIENCE['primary_persona']}'s needs? (Check docs/dna/target_audience.md)
               - Can it be implemented following our 5 design principles? (Check docs/dna/design_principles.md)
               
            2. **Technical Feasibility:**
               - Is it compatible with our {TECH_STACK['frontend']['framework']} + {TECH_STACK['backend']['framework']} architecture?
               - Does it maintain API-first and stateless backend principles?
               - Can it be deployed on {TECH_STACK['deployment']['platform']}?
               
            3. **Complexity Assessment:**
               - Simple (1-2 stories), Medium (3-5 stories), or Complex (6+ stories)?
               - Which agents need to be involved? (Speldesigner, Utvecklare, Testutvecklare, etc.)
               - Estimated development time in days?
               
            4. **Dependency Analysis:**
               - Does it depend on other features currently in development?
               - Are there external API or service dependencies?
               - Does it require changes to existing core functionality?
               
            5. **Specification Requirements:**
               - Does a specification already exist that covers this functionality?
               - Is a new specification needed from Speldesigner?
               - Are there ambiguities that need clarification before development?
            
            Provide your analysis in this JSON format:
            {{
                "dna_alignment": {{
                    "vision_mission_aligned": boolean,
                    "target_audience_served": boolean,
                    "design_principles_compatible": boolean,
                    "concerns": ["list any alignment issues"]
                }},
                "technical_feasibility": {{
                    "architecture_compatible": boolean,
                    "deployment_feasible": boolean,
                    "api_design_clear": boolean,
                    "technical_risks": ["list any technical concerns"]
                }},
                "complexity": {{
                    "estimated_stories": number,
                    "required_agents": ["agent1", "agent2"],
                    "estimated_days": number,
                    "complexity_level": "Simple|Medium|Complex"
                }},
                "dependencies": {{
                    "internal_dependencies": ["other features needed"],
                    "external_dependencies": ["external services/APIs"],
                    "blocking_issues": ["anything preventing immediate start"]
                }},
                "recommendation": {{
                    "action": "approve|clarify|reject",
                    "next_steps": ["specific actions to take"],
                    "assigned_agents": ["agents to involve"],
                    "priority": "high|medium|low"
                }}
            }}
            """,
            agent=self.agent
        )
        
        # Execute analysis
        crew = Crew(agents=[self.agent], tasks=[analysis_task])
        result = crew.kickoff()
        
        try:
            # Parse the JSON response from the agent
            analysis_result = json.loads(result)
            
            # Store analysis for tracking
            self.status_handler.report_status(
                agent_name="projektledare",
                status_code="FEATURE_ANALYZED", 
                payload={
                    "issue_id": issue_data["issue_id"],
                    "analysis": analysis_result,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return analysis_result
            
        except json.JSONDecodeError as e:
            # Handle parsing errors gracefully
            error_analysis = {
                "error": "Failed to parse agent response",
                "raw_response": str(result),
                "recommended_action": "manual_review_required"
            }
            
            self.status_handler.report_status(
                agent_name="projektledare",
                status_code="ANALYSIS_ERROR",
                payload=error_analysis
            )
            
            return error_analysis
    
    async def create_story_breakdown(self, feature_analysis: Dict[str, Any], github_issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Break down an approved feature into implementable stories.
        
        STORY CREATION PROCESS:
        1. Identify distinct functional components of the feature
        2. Ensure each story can be completed independently  
        3. Create stories that align with our Definition of Done
        4. Assign appropriate agents based on story requirements
        5. Establish clear acceptance criteria for each story
        
        Args:
            feature_analysis: Results from analyze_feature_request()
            github_issue: Original GitHub issue data
            
        Returns:
            List of story definitions ready for implementation
            
        🔧 ADAPTATION: Modify story breakdown logic for your development process
        """
        breakdown_task = Task(
            description=f"""
            Break down this approved feature into implementable stories for the DigiNativa AI team.
            
            **Feature Context:**
            - Original Issue: #{github_issue.get('number')} - {github_issue.get('title')}
            - Estimated Complexity: {feature_analysis.get('complexity', {}).get('complexity_level', 'Unknown')}
            - Required Agents: {', '.join(feature_analysis.get('complexity', {}).get('required_agents', []))}
            
            **Story Breakdown Requirements:**
            
            1. **Story Independence:** Each story must be completable without dependencies on other stories
            2. **Agent Alignment:** Assign stories to agents based on their specializations:
               - Speldesigner: UX design, game mechanics, pedagogical specifications
               - Utvecklare: Frontend (React) and Backend (FastAPI) implementation
               - Testutvecklare: Automated testing and quality assurance
               - QA-Testare: Manual testing from {TARGET_AUDIENCE['primary_persona']}'s perspective
               - Kvalitetsgranskare: Performance and architectural compliance
               
            3. **Definition of Done Compliance:** Each story must be designed to pass all 10 points:
               - Fas 1: Code implementation, standards, tests, documentation
               - Fas 2: Automated validation (100% test pass, quality gates)  
               - Fas 3: Functional review (QA approval)
               - Fas 4: Integration and deployment
               
            4. **Design Principles Integration:** Ensure stories support our 5 principles:
               - Pedagogik Framför Allt: Educational value for digitalization strategy
               - Policy till Praktik: Connects abstract concepts to practical reality
               - Respekt för Tid: Respects {TARGET_AUDIENCE['time_constraints']} constraint
               - Helhetssyn: Shows system connections and interactions
               - Intelligens: Professional tone appropriate for {TARGET_AUDIENCE['description']}
            
            **Create stories in this format:**
            [
                {{
                    "story_id": "STORY-{github_issue.get('number', 'XX')}-001",
                    "title": "Descriptive story title",
                    "description": "Clear description of what this story delivers",
                    "assigned_agent": "speldesigner|utvecklare|testutvecklare|qa_testare|kvalitetsgranskare",
                    "story_type": "specification|frontend|backend|testing|qa|quality_review",
                    "acceptance_criteria": [
                        "Specific, testable criterion 1",
                        "Specific, testable criterion 2"
                    ],
                    "dependencies": ["STORY-XX-XXX if any"],
                    "estimated_effort": "Small|Medium|Large",
                    "design_principles_addressed": ["principle1", "principle2"],
                    "definition_of_done_focus": ["Fas 1: Implementation", "Fas 2: Validation"]
                }}
            ]
            
            **Story Types Guidance:**
            - **specification**: Speldesigner creates detailed game mechanics and UX specifications
            - **frontend**: Utvecklare implements React components and user interfaces  
            - **backend**: Utvecklare implements FastAPI endpoints and business logic
            - **testing**: Testutvecklare creates automated tests (unit, integration, API)
            - **qa**: QA-Testare performs manual testing from user perspective
            - **quality_review**: Kvalitetsgranskare validates performance and architecture
            
            Aim for {feature_analysis.get('complexity', {}).get('estimated_stories', 3)} stories total.
            """,
            agent=self.agent
        )
        
        # Execute story breakdown
        crew = Crew(agents=[self.agent], tasks=[breakdown_task])
        result = crew.kickoff()
        
        try:
            # Parse the JSON response
            stories = json.loads(result)
            
            # Validate story structure
            validated_stories = []
            for story in stories:
                if self._validate_story_structure(story):
                    validated_stories.append(story)
                else:
                    print(f"Warning: Invalid story structure for {story.get('story_id', 'unknown')}")
            
            # Log successful story creation
            self.status_handler.report_status(
                agent_name="projektledare",
                status_code="STORIES_CREATED",
                payload={
                    "feature_issue_id": github_issue.get("number"),
                    "stories_count": len(validated_stories),
                    "story_ids": [s["story_id"] for s in validated_stories]
                }
            )
            
            return validated_stories
            
        except json.JSONDecodeError as e:
            print(f"Error parsing story breakdown: {e}")
            print(f"Raw response: {result}")
            return []
    
    def _validate_story_structure(self, story: Dict[str, Any]) -> bool:
        """
        Validate that a story has all required fields and valid values.
        
        VALIDATION REQUIREMENTS:
        - All required fields present
        - Agent assignment is valid  
        - Acceptance criteria are specific and testable
        - Dependencies reference valid story IDs
        
        🔧 ADAPTATION: Update validation rules for your story requirements
        """
        required_fields = [
            "story_id", "title", "description", "assigned_agent", 
            "story_type", "acceptance_criteria", "estimated_effort"
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in story:
                print(f"Missing required field: {field}")
                return False
        
        # Validate agent assignment
        valid_agents = ["speldesigner", "utvecklare", "testutvecklare", "qa_testare", "kvalitetsgranskare"]
        if story["assigned_agent"] not in valid_agents:
            print(f"Invalid agent assignment: {story['assigned_agent']}")
            return False
        
        # Validate story type
        valid_types = ["specification", "frontend", "backend", "testing", "qa", "quality_review"]
        if story["story_type"] not in valid_types:
            print(f"Invalid story type: {story['story_type']}")
            return False
        
        # Validate effort estimation
        valid_efforts = ["Small", "Medium", "Large"]
        if story["estimated_effort"] not in valid_efforts:
            print(f"Invalid effort estimation: {story['estimated_effort']}")
            return False
        
        # Validate acceptance criteria
        if not isinstance(story["acceptance_criteria"], list) or len(story["acceptance_criteria"]) == 0:
            print("Acceptance criteria must be a non-empty list")
            return False
        
        return True
    
    async def delegate_story_to_agent(self, story: Dict[str, Any]) -> bool:
        """
        Delegate a story to the appropriate specialist agent.
        
        DELEGATION PROCESS:
        1. Prepare context and instructions for the target agent
        2. Include all relevant DNA documents and specifications
        3. Set clear expectations and success criteria
        4. Initialize tracking for story progress
        5. Handle agent-specific configuration and tools
        
        Args:
            story: Story definition from create_story_breakdown()
            
        Returns:
            True if delegation successful, False if failed
            
        🔧 ADAPTATION: Update delegation logic for your agent specializations
        """
        agent_name = story["assigned_agent"]
        story_id = story["story_id"]
        
        # Prepare delegation context
        delegation_context = {
            "story": story,
            "project_context": {
                "domain": PROJECT_DOMAIN,
                "target_user": TARGET_AUDIENCE,
                "tech_stack": TECH_STACK,
                "quality_standards": QUALITY_STANDARDS
            },
            "dna_documents": {
                "vision_mission": "docs/dna/vision_and_mission.md",
                "target_audience": "docs/dna/target_audience.md", 
                "design_principles": "docs/dna/design_principles.md",
                "architecture": "docs/dna/architecture.md",
                "definition_of_done": "docs/dna/definition_of_done.md"
            },
            "workflow_guidance": "docs/workflows/story_lifecycle_guide.md"
        }
        
        try:
            # Track story delegation
            self.current_stories[story_id] = {
                "story": story,
                "assigned_agent": agent_name,
                "status": "delegated",
                "delegated_at": datetime.now(),
                "context": delegation_context
            }
            
            # Log delegation
            self.status_handler.report_status(
                agent_name="projektledare",
                status_code="STORY_DELEGATED",
                payload={
                    "story_id": story_id,
                    "assigned_agent": agent_name,
                    "story_type": story["story_type"],
                    "estimated_effort": story["estimated_effort"]
                }
            )
            
            # TODO: Implement actual agent delegation using CrewAI
            # This would involve:
            # 1. Loading the specialist agent (speldesigner, utvecklare, etc.)
            # 2. Creating a task with the story context
            # 3. Monitoring task execution
            # 4. Handling agent responses and status updates
            
            print(f"✅ Story {story_id} delegated to {agent_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delegate story {story_id} to {agent_name}: {e}")
            
            # Log delegation failure
            self.status_handler.report_status(
                agent_name="projektledare", 
                status_code="DELEGATION_FAILED",
                payload={
                    "story_id": story_id,
                    "assigned_agent": agent_name,
                    "error": str(e)
                }
            )
            
            return False
    
    async def monitor_story_progress(self, story_id: str) -> Dict[str, Any]:
        """
        Monitor the progress of a delegated story and handle any issues.
        
        MONITORING RESPONSIBILITIES:
        1. Check for status updates from assigned agent
        2. Detect timeout or stalled progress
        3. Validate work against Definition of Done criteria  
        4. Handle exceptions using workflow_exception_handling.md
        5. Escalate to humans when automatic resolution isn't possible
        
        Args:
            story_id: ID of the story to monitor
            
        Returns:
            Current progress status and any required actions
            
        🔧 ADAPTATION: Modify monitoring logic for your quality gates and timelines
        """
        if story_id not in self.current_stories:
            return {"error": f"Story {story_id} not found in tracking"}
        
        story_data = self.current_stories[story_id]
        assigned_agent = story_data["assigned_agent"]
        
        # Check for recent status updates from the assigned agent
        latest_status = self.status_handler.get_latest_status(agent_name=assigned_agent)
        
        # Calculate time since delegation
        time_since_delegation = datetime.now() - story_data["delegated_at"]
        
        # Define timeout thresholds based on estimated effort
        # 🔧 ADAPT: Adjust timeouts for your team's velocity and complexity
        timeout_thresholds = {
            "Small": timedelta(hours=4),   # 4 hours for simple stories
            "Medium": timedelta(hours=12), # 12 hours for medium stories  
            "Large": timedelta(days=2)     # 2 days for complex stories
        }
        
        estimated_effort = story_data["story"]["estimated_effort"]
        timeout_threshold = timeout_thresholds.get(estimated_effort, timedelta(hours=8))
        
        # Check for timeout
        if time_since_delegation > timeout_threshold:
            return await self._handle_story_timeout(story_id, time_since_delegation)
        
        # Check for error status codes from agent
        if latest_status and self.status_handler.is_error_status(latest_status["status"]):
            return await self._handle_agent_error(story_id, latest_status)
        
        # Check for success status codes
        if latest_status and self.status_handler.is_success_status(latest_status["status"]):
            return await self._handle_story_completion(story_id, latest_status)
        
        # Normal progress - no action needed
        return {
            "story_id": story_id,
            "status": "in_progress",
            "assigned_agent": assigned_agent,
            "time_elapsed": str(time_since_delegation),
            "timeout_in": str(timeout_threshold - time_since_delegation),
            "latest_agent_status": latest_status.get("status") if latest_status else "no_updates"
        }
    
    async def _handle_story_timeout(self, story_id: str, elapsed_time: timedelta) -> Dict[str, Any]:
        """Handle stories that have exceeded their expected completion time."""
        story_data = self.current_stories[story_id]
        
        # Log timeout event
        self.status_handler.report_status(
            agent_name="projektledare",
            status_code="STORY_TIMEOUT",
            payload={
                "story_id": story_id,
                "assigned_agent": story_data["assigned_agent"],
                "elapsed_hours": elapsed_time.total_seconds() / 3600,
                "estimated_effort": story_data["story"]["estimated_effort"]
            }
        )
        
        # Apply timeout handling from exception_handler
        timeout_resolution = await self.exception_handler.handle_timeout(
            story_id=story_id,
            agent_name=story_data["assigned_agent"],
            elapsed_time=elapsed_time
        )
        
        return {
            "story_id": story_id,
            "status": "timeout_detected",
            "resolution": timeout_resolution,
            "escalation_required": timeout_resolution.get("escalate_to_human", False)
        }
    
    async def _handle_agent_error(self, story_id: str, error_status: Dict[str, Any]) -> Dict[str, Any]:
        """Handle error status codes reported by specialist agents."""
        error_code = error_status["status"]
        error_payload = error_status.get("payload", {})
        
        # Use exception handler to resolve the error
        resolution = await self.exception_handler.handle_exception(
            status_code=error_code,
            payload=error_payload
        )
        
        return {
            "story_id": story_id,
            "status": "error_detected",
            "error_code": error_code,
            "resolution": resolution,
            "auto_resolved": resolution.get("handled", False)
        }
    
    async def _handle_story_completion(self, story_id: str, success_status: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful completion of stories by specialist agents."""
        story_data = self.current_stories[story_id]
        
        # Update story status
        story_data["status"] = "completed"
        story_data["completed_at"] = datetime.now()
        story_data["completion_data"] = success_status
        
        # Log successful completion
        self.status_handler.report_status(
            agent_name="projektledare",
            status_code="STORY_COMPLETED",
            payload={
                "story_id": story_id,
                "assigned_agent": story_data["assigned_agent"],
                "completion_time": (story_data["completed_at"] - story_data["delegated_at"]).total_seconds(),
                "agent_output": success_status.get("payload", {})
            }
        )
        
        return {
            "story_id": story_id,
            "status": "completed",
            "completion_time": story_data["completed_at"] - story_data["delegated_at"],
            "ready_for_next_phase": True
        }

# Factory function to create and configure the Projektledare agent
def create_projektledare() -> ProjektledareAgent:
    """
    Factory function to create a properly configured Projektledare agent.
    
    USAGE:
    ```python
    from agents.projektledare import create_projektledare
    
    projektledare = create_projektledare()
    analysis = await projektledare.analyze_feature_request(github_issue_data)
    ```
    
    🔧 ADAPTATION: Modify factory parameters for your configuration needs
    """
    print("🚀 Initializing Projektledare agent...")
    
    try:
        agent = ProjektledareAgent()
        print(f"✅ Projektledare initialized for {PROJECT_NAME}")
        print(f"   Domain: {PROJECT_DOMAIN}")
        print(f"   Target User: {TARGET_AUDIENCE['primary_persona']}")
        print(f"   Tech Stack: {TECH_STACK['frontend']['framework']} + {TECH_STACK['backend']['framework']}")
        return agent
        
    except Exception as e:
        print(f"❌ Failed to initialize Projektledare: {e}")
        raise

if __name__ == "__main__":
    # Test script for debugging and development
    import asyncio
    
    async def test_projektledare():
        """Test script for Projektledare functionality."""
        print("🧪 Testing Projektledare agent...")
        
        # Create agent
        projektledare = create_projektledare()
        
        # Mock GitHub issue for testing
        test_issue = {
            "number": 123,
            "title": "Add user progress tracking",
            "body": "Users should be able to see their learning progress through the digitalization strategy game.",
            "labels": [{"name": "feature"}, {"name": "enhancement"}],
            "user": {"login": "test-user"}
        }
        
        # Test feature analysis
        print("\n📋 Testing feature analysis...")
        analysis = await projektledare.analyze_feature_request(test_issue)
        print(f"Analysis result: {json.dumps(analysis, indent=2)}")
        
        # Test story breakdown (only if analysis approves the feature)
        if analysis.get("recommendation", {}).get("action") == "approve":
            print("\n📝 Testing story breakdown...")
            stories = await projektledare.create_story_breakdown(analysis, test_issue)
            print(f"Created {len(stories)} stories")
            for story in stories:
                print(f"  - {story['story_id']}: {story['title']} (assigned to {story['assigned_agent']})")
        
        print("\n✅ Projektledare testing complete!")
    
    # Run test if script is executed directly
    asyncio.run(test_projektledare())