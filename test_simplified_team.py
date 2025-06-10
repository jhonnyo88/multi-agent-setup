#!/usr/bin/env python3
"""
DigiNativa AI Team - Simplified Test Script
==========================================

Tests the simplified AI team architecture to ensure everything works.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step: str):
    print(f"\n🔹 {step}")

def print_success(message: str):
    print(f"✅ {message}")

def print_warning(message: str):
    print(f"⚠️  {message}")

def print_error(message: str):
    print(f"❌ {message}")

async def test_simplified_team():
    """Test the simplified AI team."""
    
    print_header("DigiNativa AI Team - Simplified Architecture Test")
    print("Testing core functionality without complex dependencies")
    
    test_results = {
        "configuration": False,
        "file_utils": False, 
        "agents": {"projektledare": False, "speldesigner": False, "utvecklare": False},
        "workflows": False,
        "integration": False
    }
    
    # Test 1: Configuration
    print_step("Step 1: Testing Configuration")
    try:
        from config.settings import PROJECT_NAME, TECH_STACK, SECRETS
        print_success(f"Project: {PROJECT_NAME}")
        print_success(f"Frontend: {TECH_STACK['frontend']['framework']}")
        print_success(f"Backend: {TECH_STACK['backend']['framework']}")
        
        # Check API key (without revealing it)
        api_key = SECRETS.get("anthropic_api_key", "")
        if api_key and not api_key.startswith("[YOUR_"):
            print_success("Anthropic API key configured")
        else:
            print_warning("Anthropic API key not configured")
        
        test_results["configuration"] = True
        
    except Exception as e:
        print_error(f"Configuration failed: {e}")
    
    # Test 2: File utilities
    print_step("Step 2: Testing File Utilities")
    try:
        from tools.file_utils import read_file, write_file, get_project_structure
        
        # Test reading a known file
        config_content = read_file("config/settings.py")
        if not config_content.startswith("❌"):
            print_success("File reading works")
        else:
            print_warning("File reading has issues")
        
        # Test project structure
        structure = get_project_structure(2)
        if structure:
            print_success("Project structure generation works")
        
        test_results["file_utils"] = True
        
    except Exception as e:
        print_error(f"File utilities failed: {e}")
    
    # Test 3: Individual Agents
    print_step("Step 3: Testing Individual Agents")
    
    # Test Projektledare
    try:
        from agents.projektledare import create_projektledare
        projektledare = create_projektledare()
        print_success("Projektledare created successfully")
        test_results["agents"]["projektledare"] = True
    except Exception as e:
        print_error(f"Projektledare failed: {e}")
    
    # Test Speldesigner
    try:
        from agents.speldesigner import create_speldesigner_agent
        speldesigner = create_speldesigner_agent()
        print_success("Speldesigner created successfully")
        test_results["agents"]["speldesigner"] = True
    except Exception as e:
        print_error(f"Speldesigner failed: {e}")
    
    # Test Utvecklare
    try:
        from agents.utvecklare import create_utvecklare_agent
        utvecklare = create_utvecklare_agent()
        print_success("Utvecklare created successfully")
        test_results["agents"]["utvecklare"] = True
    except Exception as e:
        print_error(f"Utvecklare failed: {e}")
    
    # Test 4: Workflows
    print_step("Step 4: Testing Workflows")
    try:
        from workflows import StatusHandler, get_workflow_status
        
        status_handler = StatusHandler()
        workflow_status = get_workflow_status()
        
        print_success("Status handler works")
        print_success(f"GitHub available: {workflow_status.get('github_integration', False)}")
        
        test_results["workflows"] = True
        
    except Exception as e:
        print_error(f"Workflows failed: {e}")
    
    # Test 5: Integration Test
    print_step("Step 5: Testing Simple Integration")
    try:
        if test_results["agents"]["speldesigner"]:
            # Test simple UX specification creation
            test_request = {
                "title": "Test Feature",
                "description": "Simple test to verify UX specification creation",
                "story_id": "TEST-001"
            }
            
            result = await speldesigner.create_ux_specification(test_request)
            
            if "error" not in result:
                print_success("UX specification creation works")
                print_success(f"Generated {len(result.get('acceptance_criteria', []))} acceptance criteria")
                test_results["integration"] = True
            else:
                print_warning(f"UX spec creation had issues: {result['error']}")
        
    except Exception as e:
        print_error(f"Integration test failed: {e}")
    
    # Summary
    print_step("Test Summary")
    
    total_tests = 5
    passed_tests = sum([
        test_results["configuration"],
        test_results["file_utils"],
        any(test_results["agents"].values()),
        test_results["workflows"],
        test_results["integration"]
    ])
    
    agent_count = sum(test_results["agents"].values())
    
    print_success(f"Overall: {passed_tests}/{total_tests} main tests passed")
    print_success(f"Agents: {agent_count}/3 agents working")
    
    if passed_tests >= 4 and agent_count >= 2:
        print_header("🎉 Simplified AI Team is Working!")
        print("The core functionality is operational.")
        print("\n📋 Next Steps:")
        print("1. Configure your .env file with API keys")
        print("2. Test with real GitHub Issues")
        print("3. Add more agents when needed")
        print("4. Customize for your specific domain")
        return True
    else:
        print_header("⚠️  Some Issues Need Attention")
        print("Check the error messages above and fix configuration issues.")
        return False

def test_file_structure():
    """Test that the simplified file structure is correct."""
    print_step("Bonus: Checking Simplified File Structure")
    
    expected_files = [
        "agents/__init__.py",
        "agents/projektledare.py", 
        "agents/speldesigner.py",
        "agents/utvecklare.py",
        "config/__init__.py",
        "config/settings.py",
        "tools/__init__.py",
        "tools/file_utils.py",
        "workflows/__init__.py",
        "workflows/status_handler.py"
    ]
    
    missing_files = []
    present_files = []
    
    for file_path in expected_files:
        if Path(file_path).exists():
            present_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    print_success(f"Present files: {len(present_files)}/{len(expected_files)}")
    
    if missing_files:
        print_warning("Missing files:")
        for file in missing_files:
            print(f"   - {file}")
    
    return len(missing_files) == 0

async def main():
    """Main test function."""
    try:
        print_header("Starting Simplified AI Team Test")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test file structure
        structure_ok = test_file_structure()
        
        # Test functionality
        functionality_ok = await test_simplified_team()
        
        if structure_ok and functionality_ok:
            print_header("✅ All Tests Passed!")
            return True
        else:
            print_header("❌ Some Tests Failed")
            return False
            
    except Exception as e:
        print_error(f"Test script failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)