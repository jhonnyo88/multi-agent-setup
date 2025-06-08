"""
Universal Tool Base for CrewAI 0.28.8 Compatibility
===================================================

PURPOSE:
Provides a universal BaseTool implementation that works across different
CrewAI versions and handles import issues gracefully.

USAGE:
Import this instead of trying to import BaseTool directly:

```python
from tools.tool_base import UniversalBaseTool as BaseTool
```
"""

from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field
import json

# Try different import strategies for maximum compatibility
TOOL_IMPLEMENTATION = None

# Strategy 1: Try CrewAI's native tool system
try:
    from crewai.tools import BaseTool
    TOOL_IMPLEMENTATION = "crewai.tools.BaseTool"
    print("✅ Using crewai.tools.BaseTool")
    
    class UniversalBaseTool(BaseTool):
        """Wrapper around CrewAI's BaseTool"""
        pass
        
except ImportError:
    # Strategy 2: Try crewai_tools package
    try:
        from crewai_tools import BaseTool
        TOOL_IMPLEMENTATION = "crewai_tools.BaseTool"
        print("✅ Using crewai_tools.BaseTool")
        
        class UniversalBaseTool(BaseTool):
            """Wrapper around crewai_tools BaseTool"""
            pass
            
    except ImportError:
        # Strategy 3: Try LangChain as fallback
        try:
            from langchain.tools import BaseTool
            TOOL_IMPLEMENTATION = "langchain.tools.BaseTool"
            print("⚠️  Using LangChain BaseTool fallback")
            
            class UniversalBaseTool(BaseTool):
                """Wrapper around LangChain's BaseTool"""
                pass
                
        except ImportError:
            # Strategy 4: Try CrewAI's Tool class
            try:
                from crewai import Tool
                TOOL_IMPLEMENTATION = "crewai.Tool"
                print("✅ Using crewai.Tool")
                
                class UniversalBaseTool(Tool):
                    """Wrapper around CrewAI's Tool class"""
                    pass
                    
            except ImportError:
                # Strategy 5: Manual implementation
                TOOL_IMPLEMENTATION = "manual"
                print("⚠️  Using manual BaseTool implementation")
                
                class UniversalBaseTool(BaseModel):
                    """
                    Manual BaseTool implementation for CrewAI 0.28.8
                    
                    This provides the essential functionality needed for tools
                    when no BaseTool is available from imports.
                    """
                    name: str = Field(..., description="Name of the tool")
                    description: str = Field(..., description="Description of what the tool does")
                    
                    def _run(self, *args, **kwargs) -> str:
                        """
                        Execute the tool's main functionality.
                        Subclasses must implement this method.
                        """
                        raise NotImplementedError("Subclasses must implement _run method")
                    
                    def run(self, *args, **kwargs) -> str:
                        """
                        Public run method that CrewAI expects.
                        This method handles the interface between CrewAI and the tool.
                        """
                        try:
                            # Handle both positional and keyword arguments
                            if args and not kwargs:
                                # Single positional argument - common case
                                if len(args) == 1:
                                    return self._run(args[0])
                                else:
                                    return self._run(*args)
                            elif kwargs and not args:
                                # Keyword arguments only
                                return self._run(**kwargs)
                            elif args and kwargs:
                                # Both - pass both
                                return self._run(*args, **kwargs)
                            else:
                                # No arguments
                                return self._run()
                        except Exception as e:
                            return f"Tool execution error: {str(e)}"
                    
                    def invoke(self, input_data: Union[str, Dict[str, Any]]) -> str:
                        """
                        Alternative invoke method for compatibility.
                        Some CrewAI versions might call this instead of run.
                        """
                        if isinstance(input_data, str):
                            return self.run(input_data)
                        elif isinstance(input_data, dict):
                            return self.run(**input_data)
                        else:
                            return self.run(input_data)
                    
                    def __call__(self, *args, **kwargs) -> str:
                        """Make the tool callable directly."""
                        return self.run(*args, **kwargs)

# Export the implementation info for debugging
def get_tool_implementation_info() -> Dict[str, Any]:
    """Get information about which tool implementation is being used."""
    return {
        "implementation": TOOL_IMPLEMENTATION,
        "base_class": UniversalBaseTool.__bases__[0].__name__ if UniversalBaseTool.__bases__ else "BaseModel",
        "available_methods": [method for method in dir(UniversalBaseTool) if not method.startswith('_')],
        "is_manual": TOOL_IMPLEMENTATION == "manual"
    }

# Convenience function for testing
def test_universal_tool():
    """Test the UniversalBaseTool implementation."""
    print(f"🧪 Testing UniversalBaseTool...")
    print(f"Implementation: {TOOL_IMPLEMENTATION}")
    
    try:
        # Create a simple test tool
        class TestTool(UniversalBaseTool):
            name: str = "Test Tool"
            description: str = "A simple test tool"
            
            def _run(self, test_input: str = "hello") -> str:
                return f"Test tool received: {test_input}"
        
        # Test the tool
        tool = TestTool()
        
        # Test different call methods
        result1 = tool.run("test1")
        result2 = tool("test2")  # __call__ method
        result3 = tool.invoke("test3")
        
        print(f"✅ Tool test results:")
        print(f"   run(): {result1}")
        print(f"   __call__(): {result2}")
        print(f"   invoke(): {result3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

if __name__ == "__main__":
    # Print implementation info
    info = get_tool_implementation_info()
    print("🔧 Tool Implementation Info:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Run test
    test_universal_tool()