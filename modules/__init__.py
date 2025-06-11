"""
DigiNativa AI-Team: Core Modules
===============================

PURPOSE: Central module registry and coordination system

MODULAR DESIGN:
- Provides unified interface to all AI team modules
- Manages module lifecycle and dependencies
- Enables dynamic module loading and configuration

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update AVAILABLE_MODULES for your agent types
2. Modify MODULE_DEPENDENCIES for your workflow
3. Adjust validation logic for your requirements

VERSION: 1.0.0
CREATED: 2025-06-10
"""

from typing import Dict, List, Any, Optional, Type
from abc import ABC, abstractmethod
import importlib
from pathlib import Path

from config.base_config import settings
from config.agent_defaults import get_agent_config, get_all_agent_types

# 🔧 ADAPT: Available modules in your system
AVAILABLE_MODULES = {
    "agents": [
        "projektledare",
        "speldesigner",    # 🔧 RENAME: For your domain
        "utvecklare", 
        "testutvecklare",
        "qa_testare",
        "kvalitetsgranskare"
    ],
    "workflows": [
        "story_lifecycle",
        "github_integration", 
        "quality_gates",
        "exception_handling"
    ],
    "tools": [
        "github_integration",
        "ai_services",
        "code_generation",
        "git_operations", 
        "deployment"
    ],
    "shared": [
        "events",
        "task_queue",
        "models", 
        "database",
        "monitoring"
    ]
}

# 🔧 ADAPT: Module dependencies for your workflow
MODULE_DEPENDENCIES = {
    "projektledare": ["github_integration", "ai_services", "task_queue", "events"],
    "speldesigner": ["ai_services", "database", "events"],  # 🔧 ADAPT: Your designer dependencies
    "utvecklare": ["ai_services", "git_operations", "code_generation", "events"],
    "testutvecklare": ["code_generation", "database", "events"],
    "qa_testare": ["github_integration", "database", "events"],
    "kvalitetsgranskare": ["deployment", "monitoring", "events"],
}

class ModuleInterface(ABC):
    """
    Base interface that all modules must implement for modular architecture.
    
    This ensures consistent module behavior and enables independent development.
    """
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize module with given configuration."""
        pass
    
    @abstractmethod
    async def process_task(self, task_input: Any) -> Any:
        """Process task according to module's contract."""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for valid inputs."""
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Return JSON schema for expected outputs."""
        pass
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Return current health and status information."""
        pass

class ModuleRegistry:
    """
    Central registry for all AI team modules.
    
    Manages module loading, dependencies, and coordination.
    """
    
    def __init__(self):
        self.loaded_modules: Dict[str, ModuleInterface] = {}
        self.module_configs: Dict[str, Dict[str, Any]] = {}
        
    def register_agent_module(self, agent_type: str, module_instance: ModuleInterface):
        """
        Register an agent module in the system.
        
        Args:
            agent_type: Type of agent (e.g., "projektledare")
            module_instance: Instance implementing ModuleInterface
        """
        if agent_type not in get_all_agent_types():
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Get agent configuration
        config = get_agent_config(agent_type)
        self.module_configs[agent_type] = config
        
        # Initialize module
        self.loaded_modules[agent_type] = module_instance
        
    async def load_module(self, module_type: str, module_name: str) -> ModuleInterface:
        """
        Dynamically load a module.
        
        Args:
            module_type: Type category (agents, workflows, tools, shared)
            module_name: Specific module name
            
        Returns:
            Loaded module instance
        """
        if module_type not in AVAILABLE_MODULES:
            raise ValueError(f"Unknown module type: {module_type}")
        
        if module_name not in AVAILABLE_MODULES[module_type]:
            raise ValueError(f"Unknown module: {module_name} in {module_type}")
        
        # Import module dynamically
        module_path = f"modules.{module_type}.{module_name}"
        module = importlib.import_module(module_path)
        
        # Get module factory or class
        if hasattr(module, f"create_{module_name}"):
            factory = getattr(module, f"create_{module_name}")
            return factory()
        elif hasattr(module, f"{module_name.title()}Module"):
            module_class = getattr(module, f"{module_name.title()}Module")
            return module_class()
        else:
            raise ImportError(f"Module {module_name} missing factory or class")
    
    async def execute_agent_task(self, agent_type: str, task_input: Any) -> Any:
        """
        Execute task on specific agent with full validation.
        
        Args:
            agent_type: Type of agent to execute
            task_input: Input data for the task
            
        Returns:
            Task execution result
        """
        if agent_type not in self.loaded_modules:
            raise ValueError(f"Agent {agent_type} not loaded")
        
        agent = self.loaded_modules[agent_type]
        
        # Validate input against agent's schema
        input_schema = agent.get_input_schema()
        self._validate_against_schema(task_input, input_schema, f"{agent_type} input")
        
        # Execute task
        result = await agent.process_task(task_input)
        
        # Validate output against agent's schema  
        output_schema = agent.get_output_schema()
        self._validate_against_schema(result, output_schema, f"{agent_type} output")
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status for all modules.
        
        Returns:
            Dictionary with status of all loaded modules
        """
        status = {
            "loaded_modules": list(self.loaded_modules.keys()),
            "available_modules": AVAILABLE_MODULES,
            "module_health": {},
            "system_ready": True
        }
        
        # Get health status from each loaded module
        for module_name, module in self.loaded_modules.items():
            try:
                health = module.get_health_status()
                status["module_health"][module_name] = health
                
                # Check if any module is unhealthy
                if not health.get("healthy", True):
                    status["system_ready"] = False
                    
            except Exception as e:
                status["module_health"][module_name] = {
                    "healthy": False,
                    "error": str(e)
                }
                status["system_ready"] = False
        
        return status
    
    def _validate_against_schema(self, data: Any, schema: Dict[str, Any], context: str):
        """
        Validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema for validation
            context: Context for error messages
        """
        # TODO: Implement proper JSON schema validation
        # For now, basic type checking
        if not isinstance(data, dict):
            raise ValueError(f"Invalid {context}: expected dict, got {type(data)}")

# Global module registry instance
registry = ModuleRegistry()

# Convenience functions for module access
async def get_agent(agent_type: str) -> ModuleInterface:
    """Get loaded agent module instance."""
    if agent_type not in registry.loaded_modules:
        # Try to load the agent dynamically
        agent = await registry.load_module("agents", agent_type)
        registry.register_agent_module(agent_type, agent)
    
    return registry.loaded_modules[agent_type]

async def execute_agent_task(agent_type: str, task_input: Any) -> Any:
    """Execute task on agent with full validation."""
    return await registry.execute_agent_task(agent_type, task_input)

def get_system_health() -> Dict[str, Any]:
    """Get current system health status."""
    return registry.get_system_status()

def list_available_agents() -> List[str]:
    """Get list of all available agent types."""
    return AVAILABLE_MODULES["agents"]

__all__ = [
    "ModuleInterface",
    "ModuleRegistry", 
    "registry",
    "get_agent",
    "execute_agent_task",
    "get_system_health",
    "list_available_agents"
]