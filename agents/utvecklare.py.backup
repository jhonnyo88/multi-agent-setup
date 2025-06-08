"""
DigiNativa AI-Agent: Utvecklare (Full-Stack Architecture Expert)
================================================================

PURPOSE:
This agent is the technical engine of the team. It receives detailed 
specifications from the Speldesigner agent and writes clean, efficient, and 
production-ready code that exactly matches the requirements. The agent is 
specialized in React and FastAPI and strictly follows the architectural 
principles defined for the project.

KEY DEPENDENCIES:
- `docs/dna/architecture.md`: The agent's bible. All technical decisions must follow this.
- `docs/dna/definition_of_done.md`: Sets the quality requirements for the produced code.
- A specification file (output from Speldesigner) as input.

ADAPTATION GUIDE:
🔧 To adapt this agent:
1.  Replace technical expertise (React, FastAPI) in `role` and `backstory` to
    match your tech stack.
2.  Adjust the "unbreakable rules" in the backstory to reflect your
    own architectural principles.
"""

from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic

from config.agent_config import get_agent_config
from config.settings import TECH_STACK
from tools.file_tools import FileReadTool, FileWriteTool
from tools.dev_tools import GitRepositoryTool
# We'll create this tool in the next step.
# from tools.architecture_tools import ArchitectureValidatorTool

class UtvecklareAgent:
    """
    The Utvecklare (Developer) agent, responsible for writing code.
    """
    def __init__(self):
        self.agent_config = get_agent_config("utvecklare")
        # Note: self.claude_llm is defined within _create_agent via the Agent class property
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """
        Creates the internal CrewAI Agent instance.
        This agent is programmed to be an expert in the project's specific
        tech stack and to follow architectural rules slavishly.
        """
        return Agent(
            role=f"Full-Stack Architecture Expert ({TECH_STACK['frontend']['framework']} & {TECH_STACK['backend']['framework']})",
            goal="""
            Transform a design specification into flawless, efficient, and production-ready code.
            You write both frontend code in React with TypeScript and backend code in FastAPI. Your work must
            be a perfect technical implementation of the given specification and follow
            ALL architectural rules without exception.
            """,
            backstory=f"""
            You are a senior full-stack developer with a passion for code quality and
            architectural purity. You are not a creative problem-solver; you are an
            exceptional technical executor. You read a specification and produce
            code that is an exact representation of it.

            Your work is governed by four UNBREAKABLE rules from the project's architecture DNA:

            1.  **Clear Separation of Concerns**: You work either in the `/frontend` or
                `/backend` directory for a given task, never both at the same time. You NEVER, under any
                circumstances, make database calls directly from the frontend.

            2.  **API-First (The Contract is King)**: You read the API contract in the specification
                and implement it precisely. You never deviate from the defined
                endpoints, request formats, or response formats.

            3.  **Stateless Backend**: All your backend code is 100% stateless. Each API call
                is an independent transaction. You never save session state on the server.

            4.  **Simplicity and Pragmatism (KISS)**: You write the simplest, most direct
                code that meets the requirements. You do not build for hypothetical future
                needs. You do not add unnecessary complexity.

            If a specification is unclear or violates these rules, you stop your work and
            immediately report the status code `FEL_SPEC_TVETYDIG_U`. All code you write
            must meet the requirements in Phase 1 of the Definition of Done.
            You are a master of TypeScript for React and use modern hooks and patterns.
            You use Tailwind CSS for styling according to the spec.
            """,
            tools=[
                FileReadTool(),
                FileWriteTool(),
                GitRepositoryTool(),
                # ArchitectureValidatorTool() # To be added in the next step
            ],
            llm=ChatAnthropic(model=self.agent_config.llm_model, temperature=self.agent_config.temperature),
            verbose=True,
            allow_delegation=False, # A developer does not delegate coding
            max_iterations=self.agent_config.max_iterations
        )

    def implement_feature(self, specification_file: str, story_id: str):
        """
        Reads a specification and implements the feature.
        """
        implementation_task = Task(
            description=f"""
            Read the UX specification from the file located at: '{specification_file}'.
            Your task is to implement the feature described in the specification.

            Follow these steps meticulously:
            1. **Read the Spec**: Use the FileReadTool to read the full content of '{specification_file}'.
            2. **Analyze**: Understand all requirements: frontend components, backend endpoints, and logic.
            3. **Create Frontend Code**: Write the React/TypeScript code for the frontend component. Save it to a file like `frontend/src/components/{story_id}.tsx`.
            4. **Create Backend Code**: Write the FastAPI/Python code for the backend endpoint. Save it to a file like `backend/app/api/{story_id}.py`.
            5. **Validate (Future Step)**: Use ArchitectureValidatorTool to ensure your code follows all rules.
            6. **Commit Code**: Use the GitRepositoryTool to create a new branch named `feature/{story_id}`, add all your created files, and commit them with the message "feat: Implement feature {story_id}". Do NOT create a pull request.
            """,
            expected_output=f"A confirmation that the code for story {story_id} has been implemented, saved to files, and committed to a new git branch named 'feature/{story_id}'.",
            agent=self.agent
        )

        # Create and run the crew
        code_crew = Crew(
            agents=[self.agent],
            tasks=[implementation_task],
            verbose=2
        )
        result = code_crew.kickoff()
        return result

def create_utvecklare_agent() -> UtvecklareAgent:
    """Factory function to create a developer agent."""
    return UtvecklareAgent()
