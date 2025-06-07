"""
Central Agent Configuration for DigiNativa AI Team
=================================================

PURPOSE:
Centralized configuration for all AI agents to enable easy tuning and optimization
of the team's behavior without modifying individual agent code.

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update MODEL_OPTIONS with your preferred AI models
2. Adjust TEMPERATURE settings for your domain's creativity requirements
3. Modify AGENT_SPECIALIZATIONS for your team structure
4. Customize QUALITY_THRESHOLDS for your quality standards
"""

from typing import Dict, Any, List
import os
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for a specific agent."""
    llm_model: str
    temperature: float
    max_tokens: int
    max_iterations: int
    specialization_focus: List[str]
    quality_threshold: float
    timeout_minutes: int

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Available AI models for different agent types
MODEL_OPTIONS = {
    "primary": "claude-3-5-sonnet-20241022",  # Best for complex reasoning
    "creative": "claude-3-5-sonnet-20241022",  # For creative/design work
    "analytical": "claude-3-5-sonnet-20241022",  # For code analysis
    "fast": "claude-3-haiku-20240307",  # For quick responses
}

# Default model selection per agent type
AGENT_MODEL_MAPPING = {
    "projektledare": MODEL_OPTIONS["primary"],    # Complex coordination
    "speldesigner": MODEL_OPTIONS["creative"],    # Creative design work
    "utvecklare": MODEL_OPTIONS["primary"],       # Complex coding
    "testutvecklare": MODEL_OPTIONS["analytical"], # Test analysis
    "qa_testare": MODEL_OPTIONS["primary"],       # User perspective
    "kvalitetsgranskare": MODEL_OPTIONS["analytical"] # Code analysis
}

# =============================================================================
# TEMPERATURE SETTINGS (CREATIVITY CONTROL)
# =============================================================================

# Temperature controls creativity vs consistency
# 0.0 = Very consistent, deterministic
# 0.3 = Balanced
# 0.7 = More creative and varied
# 1.0 = Maximum creativity

AGENT_TEMPERATURES = {
    "projektledare": 0.1,      # Need consistency in project management
    "speldesigner": 0.4,       # Need creativity for design, but focused
    "utvecklare": 0.1,         # Need consistent, reliable code
    "testutvecklare": 0.2,     # Systematic test creation
    "qa_testare": 0.3,         # Some variety in testing approaches
    "kvalitetsgranskare": 0.0  # Completely objective analysis
}

# =============================================================================
# AGENT SPECIALIZATIONS
# =============================================================================

# Key focus areas for each agent (used in prompts and validation)
AGENT_SPECIALIZATIONS = {
    "projektledare": [
        "workflow_coordination",
        "stakeholder_communication", 
        "exception_handling",
        "quality_assurance",
        "strategic_planning"
    ],
    "speldesigner": [
        "pedagogical_design",
        "user_experience",
        "game_mechanics",
        "learning_psychology",
        "accessibility",
        "swedish_public_sector_context"
    ],
    "utvecklare": [
        "react_development",
        "fastapi_backend",
        "api_design",
        "stateless_architecture",
        "performance_optimization"
    ],
    "testutvecklare": [
        "test_automation",
        "pytest_frameworks",
        "api_testing",
        "coverage_analysis",
        "ci_cd_integration"
    ],
    "qa_testare": [
        "user_acceptance_testing",
        "accessibility_testing",
        "cross_browser_testing",
        "usability_validation",
        "anna_persona_testing"
    ],
    "kvalitetsgranskare": [
        "static_code_analysis",
        "performance_testing",
        "lighthouse_audits",
        "security_scanning",
        "architecture_compliance"
    ]
}

# =============================================================================
# QUALITY THRESHOLDS
# =============================================================================

# Minimum quality scores for each agent to consider work "complete"
QUALITY_THRESHOLDS = {
    "speldesigner": {
        "design_principles_score": 0.8,  # Must score 80%+ on design principles
        "accessibility_score": 0.9,      # 90%+ accessibility compliance
        "pedagogical_effectiveness": 0.8   # 80%+ learning effectiveness
    },
    "utvecklare": {
        "code_quality_score": 0.9,       # 90%+ code quality
        "test_coverage": 0.8,             # 80%+ test coverage
        "performance_score": 0.85         # 85%+ performance
    },
    "testutvecklare": {
        "test_coverage": 0.9,             # 90%+ coverage for tests
        "test_reliability": 0.95          # 95%+ test pass rate
    },
    "qa_testare": {
        "usability_score": 0.8,           # 80%+ usability
        "accessibility_score": 0.9        # 90%+ accessibility
    },
    "kvalitetsgranskare": {
        "lighthouse_performance": 90,     # Lighthouse score > 90
        "code_quality": 0.9,              # 90%+ code quality
        "security_score": 0.95            # 95%+ security compliance
    }
}

# =============================================================================
# OPERATIONAL PARAMETERS
# =============================================================================

# Maximum iterations each agent can take on a task
MAX_ITERATIONS = {
    "projektledare": 5,      # Complex coordination may need iterations
    "speldesigner": 4,       # Creative iteration for refinement
    "utvecklare": 3,         # Should be able to code efficiently
    "testutvecklare": 3,     # Systematic test creation
    "qa_testare": 4,         # May need multiple test passes
    "kvalitetsgranskare": 2  # Objective analysis, fewer iterations
}

# Timeout limits for agent tasks (in minutes)
TIMEOUT_LIMITS = {
    "projektledare": 30,     # Complex analysis and coordination
    "speldesigner": 45,      # Creative work takes time
    "utvecklare": 60,        # Coding can be time-intensive
    "testutvecklare": 30,    # Test creation should be efficient
    "qa_testare": 45,        # Thorough testing takes time
    "kvalitetsgranskare": 15 # Automated analysis should be fast
}

# =============================================================================
# DOMAIN-SPECIFIC CONFIGURATION
# =============================================================================

# DigiNativa-specific settings (🔧 ADAPT: Change for your domain)
DOMAIN_CONFIG = {
    "primary_language": "swedish",
    "target_audience": "anna_public_sector",
    "session_time_limit": 600,  # 10 minutes max per session
    "learning_objectives": [
        "digitalization_strategy_understanding",
        "practical_implementation_skills",
        "systems_thinking_development"
    ],
    "quality_focus": [
        "pedagogical_effectiveness",
        "professional_tone",
        "time_efficiency",
        "accessibility"
    ]
}

# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def get_agent_config(agent_name: str) -> AgentConfig:
    """
    Get complete configuration for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'speldesigner', 'utvecklare')
        
    Returns:
        AgentConfig object with all settings for that agent
        
    Raises:
        ValueError: If agent_name is not recognized
    """
    if agent_name not in AGENT_MODEL_MAPPING:
        available_agents = ", ".join(AGENT_MODEL_MAPPING.keys())
        raise ValueError(f"Unknown agent '{agent_name}'. Available: {available_agents}")
    
    return AgentConfig(
        llm_model=AGENT_MODEL_MAPPING[agent_name],
        temperature=AGENT_TEMPERATURES[agent_name],
        max_tokens=4000,  # Standard for all agents
        max_iterations=MAX_ITERATIONS[agent_name],
        specialization_focus=AGENT_SPECIALIZATIONS[agent_name],
        quality_threshold=QUALITY_THRESHOLDS.get(agent_name, {}),
        timeout_minutes=TIMEOUT_LIMITS[agent_name]
    )

def get_all_agent_configs() -> Dict[str, AgentConfig]:
    """Get configuration for all agents."""
    return {
        agent_name: get_agent_config(agent_name)
        for agent_name in AGENT_MODEL_MAPPING.keys()
    }

def update_agent_temperature(agent_name: str, new_temperature: float):
    """
    Update temperature for a specific agent (for tuning).
    
    Args:
        agent_name: Name of the agent
        new_temperature: New temperature value (0.0 - 1.0)
    """
    if not 0.0 <= new_temperature <= 1.0:
        raise ValueError("Temperature must be between 0.0 and 1.0")
    
    AGENT_TEMPERATURES[agent_name] = new_temperature
    print(f"Updated {agent_name} temperature to {new_temperature}")

def get_domain_context() -> Dict[str, Any]:
    """Get domain-specific context for agent prompts."""
    return DOMAIN_CONFIG

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_agent_config(agent_name: str) -> bool:
    """
    Validate that an agent has complete configuration.
    
    Returns:
        True if configuration is complete and valid
    """
    try:
        config = get_agent_config(agent_name)
        
        # Check required fields
        required_fields = ['llm_model', 'temperature', 'max_tokens', 'max_iterations']
        for field in required_fields:
            if not hasattr(config, field):
                print(f"❌ Missing {field} for {agent_name}")
                return False
        
        # Validate temperature range
        if not 0.0 <= config.temperature <= 1.0:
            print(f"❌ Invalid temperature {config.temperature} for {agent_name}")
            return False
        
        # Validate specializations exist
        if not config.specialization_focus:
            print(f"❌ No specializations defined for {agent_name}")
            return False
        
        print(f"✅ {agent_name} configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error for {agent_name}: {e}")
        return False

def validate_all_configurations() -> bool:
    """Validate all agent configurations."""
    all_valid = True
    
    for agent_name in AGENT_MODEL_MAPPING.keys():
        if not validate_agent_config(agent_name):
            all_valid = False
    
    return all_valid

# =============================================================================
# DEBUGGING AND MONITORING
# =============================================================================

def print_agent_summary(agent_name: str):
    """Print a summary of an agent's configuration for debugging."""
    try:
        config = get_agent_config(agent_name)
        
        print(f"\n🤖 Agent Configuration Summary: {agent_name}")
        print("=" * 50)
        print(f"Model: {config.llm_model}")
        print(f"Temperature: {config.temperature}")
        print(f"Max Iterations: {config.max_iterations}")
        print(f"Timeout: {config.timeout_minutes} minutes")
        print(f"Specializations: {', '.join(config.specialization_focus)}")
        
        if config.quality_threshold:
            print("Quality Thresholds:")
            for metric, threshold in config.quality_threshold.items():
                print(f"  - {metric}: {threshold}")
        
    except Exception as e:
        print(f"❌ Could not print summary for {agent_name}: {e}")

def print_all_summaries():
    """Print configuration summaries for all agents."""
    print("🎯 DigiNativa AI Team Configuration Overview")
    print("=" * 60)
    
    for agent_name in AGENT_MODEL_MAPPING.keys():
        print_agent_summary(agent_name)
    
    print(f"\n📊 Domain Configuration:")
    for key, value in DOMAIN_CONFIG.items():
        print(f"  - {key}: {value}")

if __name__ == "__main__":
    # Test configuration when run directly
    print("🧪 Testing Agent Configuration System...")
    
    if validate_all_configurations():
        print("\n✅ All agent configurations are valid!")
        print_all_summaries()
    else:
        print("\n❌ Some agent configurations have issues!")