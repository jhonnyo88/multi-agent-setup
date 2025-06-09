"""
Debug script to isolate exactly where the 'tools' error occurs in Projektledare
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_step(step_name, test_func):
    """Helper to test each step and catch exact error location"""
    print(f"\n🧪 Testing: {step_name}")
    print("=" * 50)
    try:
        result = test_func()
        print(f"✅ {step_name}: SUCCESS")
        return result
    except Exception as e:
        print(f"❌ {step_name}: FAILED")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"   Error repr: {repr(e)}")
        print("   Full traceback:")
        traceback.print_exc(limit=10)
        return None

def test_1_basic_imports():
    """Test basic imports"""
    from agents.projektledare import Projektledare
    return "Imports OK"

def test_2_create_without_coordination():
    """Test creating Projektledare without agent coordination"""
    from agents.projektledare import Projektledare
    
    # Try to create with minimal params - NO coordination
    projektledare = Projektledare.__new__(Projektledare)  # Create instance without __init__
    return "Empty instance created"

def test_3_manual_init_step_by_step():
    """Manually step through Projektledare.__init__ to find exact failure point"""
    from agents.projektledare import Projektledare
    
    print("   🔍 Testing manual initialization...")
    
    # Create empty instance
    projektledare = Projektledare.__new__(Projektledare)
    
    # Step 1: Basic attributes
    print("   → Setting basic attributes...")
    projektledare.status_handler = None
    projektledare.github_client = None
    projektledare.claude_llm = None
    print("   ✅ Basic attributes set")
    
    # Step 2: Try to access tools attribute directly
    print("   → Testing tools attribute access...")
    try:
        tools_value = getattr(projektledare, 'tools', 'MISSING')
        print(f"   tools attribute: {tools_value}")
    except Exception as e:
        print(f"   ❌ tools attribute error: {e}")
    
    return "Manual init steps completed"

def test_4_check_agent_coordinator_import():
    """Test importing agent_coordinator separately"""
    print("   🔍 Testing agent_coordinator import...")
    
    try:
        from workflows.agent_coordinator import create_agent_coordinator
        print("   ✅ agent_coordinator import OK")
        return "Import OK"
    except Exception as e:
        print(f"   ❌ agent_coordinator import failed: {e}")
        traceback.print_exc(limit=5)
        return None

def test_5_check_agent_coordinator_creation():
    """Test creating agent_coordinator"""
    print("   🔍 Testing agent_coordinator creation...")
    
    try:
        from workflows.agent_coordinator import create_agent_coordinator
        coordinator = create_agent_coordinator()
        print(f"   ✅ coordinator created: {type(coordinator)}")
        return coordinator
    except Exception as e:
        print(f"   ❌ coordinator creation failed: {e}")
        traceback.print_exc(limit=10)
        return None

def test_6_projektledare_init_without_coordinator():
    """Test Projektledare init but skip the coordinator line"""
    print("   🔍 Testing Projektledare init without coordinator...")
    
    # Import and modify the class temporarily
    from agents.projektledare import Projektledare
    
    # Get the original __init__ method
    original_init = Projektledare.__init__
    
    def modified_init(self):
        """Modified init that skips agent_coordinator"""
        print("   → Starting modified init...")
        
        # Copy the init code but skip agent_coordinator
        from tools.github_tools import create_github_client
        from config.claude_config import get_claude_llm
        from workflows.status_handler import StatusHandler
        
        print("   → Setting up status handler...")
        self.status_handler = StatusHandler()
        
        print("   → Setting up GitHub client...")
        self.github_client = create_github_client()
        
        print("   → Setting up Claude LLM...")
        self.claude_llm = get_claude_llm()
        
        # Skip this line: self.agent_coordinator = create_agent_coordinator()
        print("   → Skipping agent_coordinator creation...")
        self.agent_coordinator = None
        
        print("   ✅ Modified init completed")
    
    # Temporarily replace the __init__ method
    Projektledare.__init__ = modified_init
    
    try:
        projektledare = Projektledare()
        print("   ✅ Projektledare created without coordinator")
        return projektledare
    except Exception as e:
        print(f"   ❌ Even modified init failed: {e}")
        traceback.print_exc(limit=5)
        return None
    finally:
        # Restore original method
        Projektledare.__init__ = original_init

def test_7_check_projektledare_source():
    """Check the actual Projektledare source code for 'tools' references"""
    print("   🔍 Scanning Projektledare source for 'tools' references...")
    
    try:
        import inspect
        from agents.projektledare import Projektledare
        
        source = inspect.getsource(Projektledare)
        lines = source.split('\n')
        
        tools_references = []
        for i, line in enumerate(lines, 1):
            if 'tools' in line.lower():
                tools_references.append(f"   Line {i}: {line.strip()}")
        
        if tools_references:
            print("   Found 'tools' references:")
            for ref in tools_references:
                print(ref)
        else:
            print("   No 'tools' references found in Projektledare source")
            
        return tools_references
    except Exception as e:
        print(f"   ❌ Source scanning failed: {e}")
        return None

def main():
    """Run all debug tests"""
    print("🚀 DEBUG: Projektledare 'tools' Error Investigation")
    print("=" * 60)
    
    results = {}
    
    # Test each step
    results['imports'] = test_step("Basic Imports", test_1_basic_imports)
    results['empty_instance'] = test_step("Create Empty Instance", test_2_create_without_coordination)
    results['manual_init'] = test_step("Manual Init Steps", test_3_manual_init_step_by_step)
    results['coordinator_import'] = test_step("Agent Coordinator Import", test_4_check_agent_coordinator_import)
    results['coordinator_creation'] = test_step("Agent Coordinator Creation", test_5_check_agent_coordinator_creation)
    results['modified_init'] = test_step("Modified Init (Skip Coordinator)", test_6_projektledare_init_without_coordinator)
    results['source_scan'] = test_step("Source Code Scan", test_7_check_projektledare_source)
    
    # Summary
    print("\n🔍 DEBUG SUMMARY")
    print("=" * 60)
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    
    print(f"Tests passed: {success_count}/{total_count}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result is not None else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print("\n💡 NEXT STEPS:")
    print("   - The first test that fails shows where the 'tools' error originates")
    print("   - Check the full traceback for the exact line causing the issue")
    print("   - Look for any CrewAI agent creation that expects a 'tools' parameter")

if __name__ == "__main__":
    main()