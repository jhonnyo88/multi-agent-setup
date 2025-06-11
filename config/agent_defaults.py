"""
DigiNativa AI-Team: Agent Default Configurations
================================================

PURPOSE: Default settings and configurations for all AI agents

MODULAR DESIGN:
- Provides consistent defaults across all agents
- Enables easy customization per agent type
- Centralizes agent behavior configuration

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update AGENT_SPECIALIZATIONS for your domain
2. Modify DEFAULT_TOOLS for your tool requirements
3. Adjust COMMUNICATION_PATTERNS for your workflow
4. Update QUALITY_STANDARDS for your requirements

VERSION: 1.0.0
CREATED: 2025-06-10
"""

from typing import Dict, List, Any
from .base_config import settings

# 🔧 ADAPT: Agent specializations for your domain
AGENT_SPECIALIZATIONS = {
    "projektledare": {
        "primary_role": "Team orchestration and project management",
        "expertise_areas": ["workflow coordination", "stakeholder communication", "quality assurance"],
        "decision_authority": "high",
        "can_delegate": True,
        "coordinates_with": ["all_agents"],
        # 🔧 ADAPT: For e-commerce: "conversion optimization", "user journey management"
        # 🔧 ADAPT: For mobile app: "app store compliance", "user retention"
    },
    
    "speldesigner": {  # 🔧 RENAME: For your domain (e.g., "product_designer", "ux_designer")
        "primary_role": "Educational game design and user experience",
        "expertise_areas": ["pedagogical design", "user experience", "learning outcomes"],
        "decision_authority": "medium",
        "can_delegate": False,
        "coordinates_with": ["projektledare", "utvecklare", "qa_testare"],
        # 🔧 ADAPT: For e-commerce: "conversion optimization", "checkout flow design"
        # 🔧 ADAPT: For mobile app: "mobile UX patterns", "app navigation"
    },
    
    "utvecklare": {
        "primary_role": "Full-stack development and code implementation",
        "expertise_areas": ["React development", "FastAPI development", "API design"],  # 🔧 ADAPT: Your tech stack
        "decision_authority": "medium",
        "can_delegate": False,
        "coordinates_with": ["speldesigner", "testutvecklare", "projektledare"],
        # 🔧 ADAPT: For different tech: "Vue.js", "Django", "Node.js", etc.
    },
    
    "testutvecklare": {
        "primary_role": "Test automation and quality assurance",
        "expertise_areas": ["automated testing", "test strategy", "quality metrics"],
        "decision_authority": "medium",
        "can_delegate": False,
        "coordinates_with": ["utvecklare", "qa_testare", "kvalitetsgranskare"],
    },
    
    "qa_testare": {
        "primary_role": "Manual testing and user perspective validation",
        "expertise_areas": ["user acceptance testing", "accessibility testing", "user experience validation"],
        "decision_authority": "medium", 
        "can_delegate": False,
        "coordinates_with": ["testutvecklare", "speldesigner", "kvalitetsgranskare"],
    },
    
    "kvalitetsgranskare": {
        "primary_role": "Code quality review and performance validation", 
        "expertise_areas": ["code review", "performance optimization", "security analysis"],
        "decision_authority": "high",
        "can_delegate": False,
        "coordinates_with": ["all_agents"],
    }
}

# 🔧 ADAPT: Default tools for your project needs
DEFAULT_TOOLS = {
    "all_agents": [
        "FileReadTool",
        "FileWriteTool", 
        "LoggingTool",
    ],
    
    "projektledare": [
        "GitHubIntegrationTool",
        "ClaudeAnalysisTool", 
        "TaskQueueTool",
        "StatusHandlerTool",
        "AgentCoordinationTool",
    ],
    
    "speldesigner": [  # 🔧 ADAPT: Tools for your domain designer
        "ClaudeSpecificationTool",
        "DesignPrinciplesValidatorTool",
        "AcceptanceCriteriaValidatorTool",
        "UserPersonaValidatorTool",  # 🔧 ADAPT: "CustomerPersonaValidatorTool" for e-commerce
    ],
    
    "utvecklare": [
        "ClaudeCodeGenerationTool",
        "GitOperationTool",
        "CodeValidatorTool",
        "APITestingTool",
        "ArchitectureValidatorTool",
    ],
    
    "testutvecklare": [
        "TestGeneratorTool",
        "CoverageAnalysisTool", 
        "TestExecutionTool",
        "PerformanceTestingTool",
    ],
    
    "qa_testare": [
        "BrowserAutomationTool",
        "AccessibilityTestingTool",
        "UserJourneyValidatorTool",
        "ManualTestingTool",
    ],
    
    "kvalitetsgranskare": [
        "CodeQualityAnalyzerTool",
        "SecurityScannerTool",
        "PerformanceProfilerTool",
        "DeploymentValidatorTool",
    ]
}

# 🔧 ADAPT: Communication patterns for your workflow
COMMUNICATION_PATTERNS = {
    "status_reporting": {
        "frequency": "after_each_task",
        "format": "structured_json",
        "include_metrics": True,
        "escalation_triggers": ["error", "timeout", "quality_failure"],
    },
    
    "inter_agent_coordination": {
        "method": "event_bus",  # 🔧 ADAPT: "direct_calls", "message_queue", etc.
        "async_preferred": True,
        "timeout_seconds": 300,
        "retry_attempts": 3,
    },
    
    "human_communication": {
        "primary_channel": "github_issues",  # 🔧 ADAPT: Your communication channel
        "notification_events": ["completion", "error", "approval_needed"],
        "update_frequency": "significant_progress",
    }
}

# 🔧 ADAPT: Quality standards for your project
QUALITY_STANDARDS = {
    "code_quality": {
        "style_guide": "black_formatted",  # 🔧 ADAPT: Your style guide
        "type_checking": "strict",
        "documentation": "comprehensive_docstrings",
        "complexity_limit": 10,
    },
    
    "testing_requirements": {
        "unit_test_coverage": 0.90,
        "integration_test_coverage": 0.80,
        "e2e_test_coverage": "critical_paths",
        "performance_test_required": True,
    },
    
    "delivery_standards": {
        "all_tests_pass": True,
        "no_security_vulnerabilities": True,
        "performance_meets_targets": True,
        "accessibility_compliant": True,
        "documentation_complete": True,
    }
}

# 🔧 ADAPT: Workflow timeouts for your process
WORKFLOW_TIMEOUTS = {
    "feature_analysis": 600,      # 10 minutes
    "specification_creation": 1800,  # 30 minutes
    "code_implementation": 3600,     # 1 hour
    "test_creation": 1800,          # 30 minutes  
    "qa_validation": 1200,          # 20 minutes
    "quality_review": 900,          # 15 minutes
}

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """
    Get complete configuration for a specific agent type.
    
    Args:
        agent_type: Type of agent (e.g., "projektledare", "speldesigner")
        
    Returns:
        Complete configuration dictionary for the agent
    """
    if agent_type not in AGENT_SPECIALIZATIONS:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    base_tools = DEFAULT_TOOLS.get("all_agents", [])
    agent_tools = DEFAULT_TOOLS.get(agent_type, [])
    
    return {
        "agent_type": agent_type,
        "specialization": AGENT_SPECIALIZATIONS[agent_type],
        "tools": base_tools + agent_tools,
        "communication": COMMUNICATION_PATTERNS,
        "quality_standards": QUALITY_STANDARDS,
        "timeouts": WORKFLOW_TIMEOUTS,
        "project_settings": {
            "domain": settings.project_domain,
            "ai_model": settings.default_ai_model,
            "quality_gates": settings.quality_gates,
        }
    }

def get_all_agent_types() -> List[str]:
    """Get list of all available agent types."""
    return list(AGENT_SPECIALIZATIONS.keys())

def validate_agent_config(agent_type: str) -> bool:
    """
    Validate that agent configuration is complete and consistent.
    
    Args:
        agent_type: Type of agent to validate
        
    Returns:
        True if configuration is valid
    """
    try:
        config = get_agent_config(agent_type)
        
        # Check required fields
        required_fields = ["specialization", "tools", "communication", "quality_standards"]
        for field in required_fields:
            if field not in config:
                return False
        
        # Check specialization completeness
        specialization = config["specialization"]
        required_spec_fields = ["primary_role", "expertise_areas", "decision_authority"]
        for field in required_spec_fields:
            if field not in specialization:
                return False
        
        return True
        
    except Exception:
        return False