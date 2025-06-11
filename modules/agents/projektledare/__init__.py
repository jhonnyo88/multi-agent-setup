"""
Projektledare Agent Module
=========================

PURPOSE: Team orchestrator and project management agent

PUBLIC INTERFACE: This is the only way other modules interact with Projektledare

GUARANTEED CONTRACT:
- Input: ProjektledareRequest (see contracts/input_models.py)
- Output: ProjektledareResponse (see contracts/output_models.py)
- All internal implementation can change without breaking system

MODULAR PROMISE:
- This entire module can be rewritten for improvements
- Internal logic can be completely changed
- Only contracts must remain compatible
- Dependencies are clearly defined and minimal

USAGE:
    from modules.agents.projektledare import ProjektledareAgent, create_projektledare
    
    agent = create_projektledare()
    result = await agent.analyze_feature_request(github_issue)

VERSION: 1.0.0
CREATED: 2025-06-10
"""

from .agent import ProjektledareAgent
from .contracts.input_models import (
    FeatureAnalysisRequest,
    StoryCreationRequest,
    TeamCoordinationRequest
)
from .contracts.output_models import (
    FeatureAnalysisResponse,
    StoryCreationResponse, 
    TeamCoordinationResponse
)

# Public interface - only these are exposed to other modules
__all__ = [
    'ProjektledareAgent',
    'create_projektledare',
    'FeatureAnalysisRequest',
    'FeatureAnalysisResponse',
    'StoryCreationRequest',
    'StoryCreationResponse',
    'TeamCoordinationRequest',
    'TeamCoordinationResponse'
]

# Module metadata for introspection
__version__ = "1.0.0"
__agent_type__ = "projektledare"
__capabilities__ = [
    "feature_analysis",
    "story_breakdown", 
    "team_coordination",
    "workflow_orchestration",
    "exception_handling"
]

def create_projektledare(custom_config: dict = None) -> ProjektledareAgent:
    """
    Factory function for creating Projektledare agent instances.
    
    Args:
        custom_config: Optional custom configuration overrides
        
    Returns:
        Configured ProjektledareAgent instance
        
    Example:
        # Standard agent
        agent = create_projektledare()
        
        # Custom configuration  
        agent = create_projektledare({
            "ai_model": "gpt-4-turbo",
            "analysis_depth": "comprehensive"
        })
    """
    from config.agent_defaults import get_agent_config
    
    # Get default configuration
    config = get_agent_config("projektledare")
    
    # Apply custom overrides
    if custom_config:
        config.update(custom_config)
    
    return ProjektledareAgent(config)

def validate_module_contract():
    """
    Validate that this module meets its interface contract.
    
    This runs at module import to ensure contract compliance.
    """
    # Verify all required classes exist
    required_classes = [
        'ProjektledareAgent',
        'FeatureAnalysisRequest',
        'FeatureAnalysisResponse'
    ]
    
    for class_name in required_classes:
        if class_name not in globals():
            raise ImportError(f"Required class {class_name} not found in Projektledare module")
    
    # Verify agent has required methods
    agent = ProjektledareAgent({})
    required_methods = ['analyze_feature_request', 'create_story_breakdown', 'coordinate_team']
    
    for method_name in required_methods:
        if not hasattr(agent, method_name):
            raise AttributeError(f"ProjektledareAgent missing required method: {method_name}")

# Validate contract on import
validate_module_contract()