#!/usr/bin/env python3
"""
Debug script to diagnose CrewAI tool issues
"""

def debug_crewai_tools():
    """Debug CrewAI tool loading issues."""
    print("🔧 Debugging CrewAI Tool Issues...")
    
    # Test 1: CrewAI imports
    print("\n1. Testing CrewAI imports...")
    try:
        from crewai import Agent, Task, Crew
        print("✅ CrewAI imports successful")
        
        # Check Agent constructor signature
        import inspect
        agent_sig = inspect.signature(Agent.__init__)
        print(f"Agent.__init__ signature: {agent_sig}")
        
    except Exception as e:
        print(f"❌ CrewAI import failed: {e}")
        return
    
    # Test 2: Tool imports
    print("\n2. Testing tool imports...")
    tools_status = {}
    
    try:
        from tools.file_utils import read_file, write_file
        tools_status["file_tools"] = "✅ OK"
    except Exception as e:
        tools_status["file_tools"] = f"❌ {e}"
    
    try:
        from tools.design_tools import DesignPrinciplesValidatorTool
        tools_status["design_tools"] = "✅ OK"
    except Exception as e:
        tools_status["design_tools"] = f"❌ {e}"
    
    try:
        from tools.context_tools import FileSearchTool
        tools_status["context_tools"] = "✅ OK"
    except Exception as e:
        tools_status["context_tools"] = f"❌ {e}"
    
    for tool_name, status in tools_status.items():
        print(f"   {tool_name}: {status}")
    
    # Test 3: Tool creation
    print("\n3. Testing tool creation...")
    try:
        from tools.file_utils import read_file, write_file
        
        file_read_tool = FileReadTool()
        print(f"✅ FileReadTool created: {type(file_read_tool)}")
        
        file_write_tool = FileWriteTool()
        print(f"✅ FileWriteTool created: {type(file_write_tool)}")
        
        # Test tool attributes
        print(f"   FileReadTool attributes: {dir(file_read_tool)}")
        
    except Exception as e:
        print(f"❌ Tool creation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Agent creation with tools
    print("\n4. Testing Agent creation...")
    try:
        from langchain_anthropic import ChatAnthropic
        from config.settings import SECRETS, AGENT_CONFIG
        
        # Create Claude LLM
        claude_llm = ChatAnthropic(
            model=AGENT_CONFIG["llm_model"],
            api_key=SECRETS.get("anthropic_api_key"),
            temperature=0.1,
            max_tokens_to_sample=1000
        )
        print("✅ Claude LLM created")
        
        # Test with empty tools list
        agent_empty = Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
            tools=[],  # Empty tools list
            llm=claude_llm,
            verbose=False
        )
        print("✅ Agent with empty tools created successfully")
        
        # Test with single tool
        from tools.file_tools import FileReadTool
        single_tool = FileReadTool()
        
        agent_single_tool = Agent(
            role="Test Agent",
            goal="Test goal", 
            backstory="Test backstory",
            tools=[single_tool],  # Single tool
            llm=claude_llm,
            verbose=False
        )
        print("✅ Agent with single tool created successfully")
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Minimal Speldesigner creation
    print("\n5. Testing minimal Speldesigner creation...")
    try:
        from langchain_anthropic import ChatAnthropic
        from config.settings import SECRETS, AGENT_CONFIG
        
        claude_llm = ChatAnthropic(
            model=AGENT_CONFIG["llm_model"],
            api_key=SECRETS.get("anthropic_api_key"),
            temperature=0.4,
            max_tokens_to_sample=4000
        )
        
        minimal_agent = Agent(
            role="Minimal Speldesigner",
            goal="Create UX specifications",
            backstory="You are a UX designer.",
            tools=[],  # No tools to avoid issues
            llm=claude_llm,
            verbose=True,
            allow_delegation=False,
            max_iterations=3
        )
        print("✅ Minimal Speldesigner agent created successfully")
        
    except Exception as e:
        print(f"❌ Minimal Speldesigner creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_crewai_tools()