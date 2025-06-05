"""
DigiNativa AI Agents Package
============================

PURPOSE:
This package contains all AI agents that make up the DigiNativa development team.
Each agent is a specialist with specific responsibilities and capabilities.

ADAPTATION GUIDE:
🔧 To adapt these agents for your project:
1. Update agent roles and specializations for your domain
2. Modify agent prompts and backstories for your technical stack
3. Adjust agent tools and capabilities for your workflow
4. Customize agent communication patterns for your coordination needs

AGENT ARCHITECTURE:
Each agent follows a consistent pattern:
- Inherits from CrewAI Agent with domain-specific configuration
- Has specialized tools for their responsibilities
- Follows project DNA documents for decision-making
- Reports status using standardized codes
- Handles exceptions according to documented procedures

AVAILABLE AGENTS:
- Projektledare: Central orchestrator and team coordinator
- Speldesigner: Game mechanics and UX specialist (🔧 ADAPT: Your domain designer)
- Utvecklare: Full-stack developer (React + FastAPI)
- Testutvecklare: Test automation engineer
- QA-Testare: Manual testing from user perspective
- Kvalitetsgranskare: Code quality and performance reviewer

USAGE:
```python
from agents import create_projektledare, create_speldesigner

# Create agents
pm = create_projektledare()
designer = create_speldesigner()

# Use in workflows
analysis = await pm.analyze_feature_request(github_issue)
spec = await designer.create_specification(analysis)
```
"""

from .projektledare import create_projektledare, ProjektledareAgent

# TODO: Import other agents as they are implemented
# from .speldesigner import create_speldesigner, SpeldesignerAgent
# from .utvecklare import create_utvecklare, UtvecklareAgent
# from .testutvecklare import create_testutvecklare, TestutvecklareAgent
# from .qa_testare import create_qa_testare, QATestareAgent
# from .kvalitetsgranskare import create_kvalitetsgranskare, KvalitetsgranskareAgent

__all__ = [
    "create_projektledare",
    "ProjektledareAgent",
    # TODO: Add other agents as they are implemented
    # "create_speldesigner",
    # "SpeldesignerAgent",
    # "create_utvecklare", 
    # "UtvecklareAgent",
    # "create_testutvecklare",
    # "TestutvecklareAgent",
    # "create_qa_testare",
    # "QATestareAgent",
    # "create_kvalitetsgranskare",
    # "KvalitetsgranskareAgent"
]

# Agent metadata for introspection and tooling
AGENT_METADATA = {
    "projektledare": {
        "role": "Team Orchestrator",
        "specialization": "Project management, workflow coordination, exception handling",
        "tools": ["FileReadTool", "FileWriteTool", "GitTool"],
        "can_delegate": True,
        "coordinates_with": ["all agents"],
        "domain_focus": "Process management and quality assurance"
    },
    # TODO: Add metadata for other agents
    # "speldesigner": {
    #     "role": "Game Designer & UX Specialist", 
    #     "specialization": "Pedagogical game design, user experience, learning outcomes",
    #     "tools": ["FileReadTool", "FileWriteTool", "DesignPrinciplesTool"],
    #     "can_delegate": False,
    #     "coordinates_with": ["projektledare", "utvecklare", "qa_testare"],
    #     "domain_focus": "Educational game mechanics and user experience"
    # }
}

def get_available_agents():
    """
    Get list of currently available agents.
    
    Returns:
        List of agent names that are implemented and available for use
        
    🔧 ADAPTATION: Update this list as you implement agents for your domain
    """
    return ["projektledare"]  # TODO: Add other agents as implemented

def get_agent_metadata(agent_name: str):
    """
    Get metadata about a specific agent.
    
    Args:
        agent_name: Name of the agent to get metadata for
        
    Returns:
        Dictionary with agent metadata or None if agent not found
    """
    return AGENT_METADATA.get(agent_name)

def create_agent_by_name(agent_name: str):
    """
    Factory function to create any agent by name.
    
    Args:
        agent_name: Name of the agent to create
        
    Returns:
        Initialized agent instance
        
    Raises:
        ValueError: If agent name is not recognized
        
    🔧 ADAPTATION: Add your agents to this factory function
    """
    agent_factories = {
        "projektledare": create_projektledare,
        # TODO: Add other agent factories
        # "speldesigner": create_speldesigner,
        # "utvecklare": create_utvecklare,
        # "testutvecklare": create_testutvecklare,
        # "qa_testare": create_qa_testare,
        # "kvalitetsgranskare": create_kvalitetsgranskare
    }
    
    if agent_name not in agent_factories:
        available = ", ".join(agent_factories.keys())
        raise ValueError(f"Unknown agent '{agent_name}'. Available agents: {available}")
    
    return agent_factories[agent_name]()