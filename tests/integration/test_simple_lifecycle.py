#!/usr/bin/env python3
"""
Simple Lifecycle Test - Fast version without agent initialization loops
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

def test_simple_file_operations():
    """Test basic file operations without agent initialization."""
    print("🧪 Testing simple file operations...")
    
    try:
        from tools.file_tools import read_file, write_file
        
        # Test file writing
        test_content = "# Test file\nThis is a test."
        result = write_file("reports/test_simple.md", test_content, "test_runner")
        
        assert "successfully" in result.lower()
        print("✅ File operations working")
        return True
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return False

def test_basic_imports():
    """Test that we can import basic modules."""
    print("🧪 Testing basic imports...")
    
    try:
        from config.settings import PROJECT_NAME
        print(f"✅ Config import working - Project: {PROJECT_NAME}")
        
        from tools.file_tools import FileReadTool
        print("✅ Tools import working")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

@patch('workflows.agent_coordinator.create_agent_coordinator')
@patch('agents.speldesigner.create_speldesigner_agent')
@patch('agents.utvecklare.create_utvecklare_agent') 
@patch('agents.testutvecklare.create_testutvecklare_agent')
@patch('agents.qa_testare.create_qa_testare_agent')
@patch('agents.kvalitetsgranskare.create_kvalitetsgranskare_agent')
def test_projektledare_creation_mocked(*mocks):
    """Test projektledare creation with all dependencies mocked."""
    print("🧪 Testing mocked projektledare creation...")
    
    try:
        # Mock all the agent creation functions
        for mock in mocks:
            mock.return_value = MagicMock()
        
        from agents.projektledare import ProjektledareAgent
        
        # Create projektledare without coordinator (which causes the loop)
        projektledare = ProjektledareAgent()
        
        assert projektledare is not None
        print("✅ Mocked projektledare creation working")
        return True
        
    except Exception as e:
        print(f"❌ Projektledare creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running simple lifecycle tests...")
    
    success_count = 0
    
    if test_basic_imports():
        success_count += 1
    
    if test_simple_file_operations():
        success_count += 1
        
    if test_projektledare_creation_mocked():
        success_count += 1
    
    print(f"\n🎉 Simple tests completed: {success_count}/3 successful")
    
    if success_count == 3:
        print("✅ All basic functionality working!")
    else:
        print("⚠️  Some issues found - let's debug step by step")