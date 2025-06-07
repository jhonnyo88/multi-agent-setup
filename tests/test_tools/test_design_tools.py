#!/usr/bin/env python3
"""
Test Suite for DigiNativa Design Tools
=====================================

PURPOSE:
Comprehensive testing of all design validation tools to ensure they work
correctly with both AI-powered and fallback validation modes.

WHAT THIS TESTS:
1. Design Principles Validator Tool functionality
2. Acceptance Criteria Validator Tool functionality  
3. Anna Persona Validator Tool functionality
4. Integration with Claude API (when available)
5. Fallback mode when AI is unavailable
6. Error handling and edge cases

HOW TO RUN:
    python tests/test_design_tools.py
    
EXPECTED OUTPUT:
- Validation of all tool imports and initialization
- Test of AI-powered validation (if API key available)
- Test of fallback validation modes
- Performance and reliability metrics
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.design_tools import (
        DesignPrinciplesValidatorTool,
        AcceptanceCriteriaValidatorTool,
        AnnaPersonaValidatorTool,
        test_all_design_tools
    )
    from config.settings import SECRETS
    print("✅ Successfully imported design tools")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def print_section(title: str):
    """Print clear test section headers."""
    print(f"\n{'='*70}")
    print(f"🧪 {title}")
    print(f"{'='*70}")

def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")

def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")

def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message."""
    print(f"⚠️  {message}")

class DesignToolsTestSuite:
    """Comprehensive test suite for design validation tools."""
    
    def __init__(self):
        self.test_results = {
            "tool_initialization": False,
            "design_principles_validation": False,
            "acceptance_criteria_validation": False,
            "anna_persona_validation": False,
            "error_handling": False,
            "performance": False
        }
        
        # Test data
        self.sample_specification = """
        # User Progress Tracking Interface Specification
        
        ## Overview
        This feature provides Anna with a clear, professional interface to track her
        learning progress through the DigiNativa digitalization strategy game.
        
        ## Visual Design
        - Professional Swedish institutional design aesthetic
        - Primary color: #0066CC (institutional blue)
        - Accent color: #00AA44 (progress green)
        - Typography: Clean sans-serif with accessible contrast ratios
        - Layout: Responsive card-based design optimized for mobile-first
        
        ## User Experience Flow
        1. Anna accesses progress from main dashboard
        2. Views completion percentage in clear progress bar
        3. Sees list of completed topics with checkmarks
        4. Reviews time invested in learning activities
        5. Quick access to continue learning from last position
        
        ## Game Mechanics
        - Progress visualization shows percentage completion
        - Achievement indicators for completed modules
        - Time tracking shows investment in learning
        - Motivational elements encourage continued engagement
        
        ## Accessibility
        - Screen reader compatible with proper ARIA labels
        - Keyboard navigation support for all interactive elements
        - High contrast mode available for visual accessibility
        - Text scaling support up to 200% without layout breaking
        
        ## Performance
        - Initial load time under 2 seconds on 3G connection
        - Responsive interactions with <100ms feedback
        - Optimized for Swedish public sector network conditions
        
        ## Educational Value
        Progress tracking serves pedagogical purpose by:
        - Reinforcing learning achievements and building confidence
        - Showing connection between time invested and competency gained
        - Encouraging systematic progression through strategy topics
        - Providing data for Anna to demonstrate learning ROI to management
        """
        
        self.sample_acceptance_criteria = [
            "Progress bar displays current completion percentage with accurate calculation",
            "Completed topics are visually marked with green checkmarks",
            "Time spent learning is shown in human-readable format (hours and minutes)",
            "Interface loads completely within 2 seconds on desktop and mobile",
            "All interactive elements have minimum 44px touch targets for mobile accessibility",
            "Progress data persists between user sessions without data loss",
            "User can navigate back to main dashboard from any point in progress view",
            "Screen reader announces progress information in logical reading order",
            "Interface maintains visual hierarchy and readability at 200% zoom level",
            "Progress updates are saved automatically without requiring user action"
        ]
        
        self.sample_poor_criteria = [
            "It should work well",
            "Users like it",
            "Fast enough",
            "Looks good",
            "Easy to use"
        ]

    async def run_all_tests(self) -> Dict[str, bool]:
        """Run the complete test suite."""
        print_section("DigiNativa Design Tools - Comprehensive Test Suite")
        print_info("Testing design validation tools for Speldesigner agent")
        print_info("This verifies tool functionality with both AI and fallback modes")
        
        # Check API availability
        api_available = self._check_api_availability()
        
        # Run individual tests
        await self.test_tool_initialization()
        await self.test_design_principles_validation()
        await self.test_acceptance_criteria_validation()
        await self.test_anna_persona_validation()
        await self.test_error_handling()
        await self.test_performance()
        
        return self.test_results

    def _check_api_availability(self) -> bool:
        """Check if Anthropic API is available."""
        api_key = SECRETS.get("anthropic_api_key")
        available = api_key and not api_key.startswith("[YOUR_")
        
        if available:
            print_info("🤖 Claude API available - testing AI-powered validation")
        else:
            print_warning("⚙️  Claude API not available - testing fallback mode only")
        
        return available

    async def test_tool_initialization(self):
        """Test that all tools can be initialized correctly."""
        print_section("Test 1: Tool Initialization")
        
        try:
            # Test Design Principles Validator initialization
            print_info("Initializing Design Principles Validator...")
            principles_tool = DesignPrinciplesValidatorTool()
            assert hasattr(principles_tool, 'name')
            assert hasattr(principles_tool, 'description')
            assert hasattr(principles_tool, '_run')
            print_success("Design Principles Validator initialized")
            
            # Test Acceptance Criteria Validator initialization
            print_info("Initializing Acceptance Criteria Validator...")
            criteria_tool = AcceptanceCriteriaValidatorTool()
            assert hasattr(criteria_tool, 'name')
            assert hasattr(criteria_tool, 'description')
            assert hasattr(criteria_tool, '_run')
            print_success("Acceptance Criteria Validator initialized")
            
            # Test Anna Persona Validator initialization
            print_info("Initializing Anna Persona Validator...")
            persona_tool = AnnaPersonaValidatorTool()
            assert hasattr(persona_tool, 'name')
            assert hasattr(persona_tool, 'description')
            assert hasattr(persona_tool, '_run')
            print_success("Anna Persona Validator initialized")
            
            print_success("All design tools initialized successfully")
            self.test_results["tool_initialization"] = True
            
        except Exception as e:
            print_error(f"Tool initialization failed: {e}")
            self.test_results["tool_initialization"] = False

    async def test_design_principles_validation(self):
        """Test Design Principles Validator with sample specification."""
        print_section("Test 2: Design Principles Validation")
        
        try:
            print_info("Testing design principles validation...")
            
            # Initialize tool
            validator = DesignPrinciplesValidatorTool()
            
            # Run validation
            result = validator._run(self.sample_specification)
            
            # Parse and validate result
            validation_data = json.loads(result)
            
            # Check required fields
            required_fields = [
                "principle_1_pedagogy",
                "principle_2_policy_to_practice", 
                "principle_3_time_respect",
                "principle_4_holistic_view",
                "principle_5_intelligence_not_infantilization",
                "overall_score"
            ]
            
            for field in required_fields:
                assert field in validation_data, f"Missing field: {field}"
                
                if field != "overall_score":
                    principle_data = validation_data[field]
                    assert "score" in principle_data, f"Missing score in {field}"
                    assert "reasoning" in principle_data, f"Missing reasoning in {field}"
                    
                    score = principle_data["score"]
                    assert 1 <= score <= 5, f"Invalid score {score} in {field}"
            
            # Check overall score
            overall_score = validation_data["overall_score"]
            assert 0.0 <= overall_score <= 1.0, f"Invalid overall score: {overall_score}"
            
            print_success("Design principles validation completed successfully")
            print_info(f"Overall validation score: {overall_score:.2f}")
            
            # Print sample results
            print_info("Sample validation results:")
            for field in required_fields[:2]:  # Show first 2 principles
                if field != "overall_score":
                    principle = validation_data[field]
                    print_info(f"  {field}: {principle['score']}/5 - {principle['reasoning'][:60]}...")
            
            self.test_results["design_principles_validation"] = True
            
        except Exception as e:
            print_error(f"Design principles validation failed: {e}")
            self.test_results["design_principles_validation"] = False

    async def test_acceptance_criteria_validation(self):
        """Test Acceptance Criteria Validator with good and poor criteria."""
        print_section("Test 3: Acceptance Criteria Validation")
        
        try:
            print_info("Testing acceptance criteria validation...")
            
            # Initialize tool
            validator = AcceptanceCriteriaValidatorTool()
            
            # Test with good criteria
            print_info("Testing with well-written criteria...")
            good_result = validator._run(self.sample_acceptance_criteria)
            good_data = json.loads(good_result)
            
            assert isinstance(good_data, list), "Result should be a list"
            assert len(good_data) == len(self.sample_acceptance_criteria), "Should validate all criteria"
            
            # Check structure of results
            for item in good_data:
                required_fields = ["criterion", "is_testable", "is_specific", "is_measurable", "overall_quality"]
                for field in required_fields:
                    assert field in item, f"Missing field: {field}"
            
            print_success("Good criteria validation completed")
            
            # Test with poor criteria
            print_info("Testing with poorly-written criteria...")
            poor_result = validator._run(self.sample_poor_criteria)
            poor_data = json.loads(poor_result)
            
            assert isinstance(poor_data, list), "Result should be a list"
            assert len(poor_data) == len(self.sample_poor_criteria), "Should validate all criteria"
            
            print_success("Poor criteria validation completed")
            
            # Compare results
            good_quality_count = sum(1 for item in good_data if item.get("overall_quality") in ["good", "excellent"])
            poor_quality_count = sum(1 for item in poor_data if item.get("overall_quality") in ["poor", "fair"])
            
            print_info(f"Good criteria: {good_quality_count}/{len(good_data)} rated as good/excellent")
            print_info(f"Poor criteria: {poor_quality_count}/{len(poor_data)} rated as poor/fair")
            
            # Tool should distinguish between good and poor criteria
            assert good_quality_count > poor_quality_count, "Tool should distinguish quality levels"
            
            self.test_results["acceptance_criteria_validation"] = True
            
        except Exception as e:
            print_error(f"Acceptance criteria validation failed: {e}")
            self.test_results["acceptance_criteria_validation"] = False

    async def test_anna_persona_validation(self):
        """Test Anna Persona Validator with sample specification."""
        print_section("Test 4: Anna Persona Validation")
        
        try:
            print_info("Testing Anna persona validation...")
            
            # Initialize tool
            validator = AnnaPersonaValidatorTool()
            
            # Run validation
            result = validator._run(self.sample_specification)
            validation_data = json.loads(result)
            
            # Check required fields
            required_fields = [
                "anna_alignment_score",
                "time_respect",
                "professional_tone", 
                "practical_value",
                "usability",
                "recommendations",
                "validation_summary"
            ]
            
            for field in required_fields:
                assert field in validation_data, f"Missing field: {field}"
            
            # Check score fields structure
            score_fields = ["time_respect", "professional_tone", "practical_value", "usability"]
            for field in score_fields:
                score_data = validation_data[field]
                assert "score" in score_data, f"Missing score in {field}"
                assert "reasoning" in score_data, f"Missing reasoning in {field}"
                
                score = score_data["score"]
                assert 1 <= score <= 5, f"Invalid score {score} in {field}"
            
            # Check overall alignment score
            alignment_score = validation_data["anna_alignment_score"]
            assert 0.0 <= alignment_score <= 1.0, f"Invalid alignment score: {alignment_score}"
            
            # Check recommendations
            recommendations = validation_data["recommendations"]
            assert isinstance(recommendations, list), "Recommendations should be a list"
            
            print_success("Anna persona validation completed successfully")
            print_info(f"Anna alignment score: {alignment_score:.2f}")
            print_info(f"Number of recommendations: {len(recommendations)}")
            
            self.test_results["anna_persona_validation"] = True
            
        except Exception as e:
            print_error(f"Anna persona validation failed: {e}")
            self.test_results["anna_persona_validation"] = False

    async def test_error_handling(self):
        """Test error handling with invalid inputs."""
        print_section("Test 5: Error Handling")
        
        try:
            print_info("Testing error handling with invalid inputs...")
            
            # Test with empty specification
            print_info("Testing with empty specification...")
            validator = DesignPrinciplesValidatorTool()
            empty_result = validator._run("")
            empty_data = json.loads(empty_result)
            
            # Should still return valid structure even with empty input
            assert "overall_score" in empty_data, "Should handle empty input gracefully"
            print_success("Empty input handled correctly")
            
            # Test with invalid criteria list
            print_info("Testing with empty criteria list...")
            criteria_validator = AcceptanceCriteriaValidatorTool()
            empty_criteria_result = criteria_validator._run([])
            empty_criteria_data = json.loads(empty_criteria_result)
            
            assert isinstance(empty_criteria_data, list), "Should return list even for empty input"
            print_success("Empty criteria list handled correctly")
            
            # Test with very long input (edge case)
            print_info("Testing with very long specification...")
            long_spec = "Very long specification. " * 1000  # 5000+ words
            long_result = validator._run(long_spec)
            long_data = json.loads(long_result)
            
            assert "overall_score" in long_data, "Should handle long input gracefully"
            print_success("Long input handled correctly")
            
            self.test_results["error_handling"] = True
            
        except Exception as e:
            print_error(f"Error handling test failed: {e}")
            self.test_results["error_handling"] = False

    async def test_performance(self):
        """Test performance and response times."""
        print_section("Test 6: Performance Testing")
        
        try:
            print_info("Testing tool performance...")
            
            import time
            
            # Test Design Principles Validator performance
            print_info("Measuring Design Principles Validator performance...")
            start_time = time.time()
            
            validator = DesignPrinciplesValidatorTool()
            result = validator._run(self.sample_specification)
            
            end_time = time.time()
            principles_duration = end_time - start_time
            
            print_info(f"Design Principles validation took {principles_duration:.2f} seconds")
            
            # Test Acceptance Criteria Validator performance
            print_info("Measuring Acceptance Criteria Validator performance...")
            start_time = time.time()
            
            criteria_validator = AcceptanceCriteriaValidatorTool()
            criteria_result = criteria_validator._run(self.sample_acceptance_criteria)
            
            end_time = time.time()
            criteria_duration = end_time - start_time
            
            print_info(f"Acceptance Criteria validation took {criteria_duration:.2f} seconds")
            
            # Performance thresholds (reasonable for both AI and fallback modes)
            max_duration = 30.0  # 30 seconds max (allows for API calls)
            
            assert principles_duration < max_duration, f"Design validation too slow: {principles_duration:.2f}s"
            assert criteria_duration < max_duration, f"Criteria validation too slow: {criteria_duration:.2f}s"
            
            print_success("Performance tests passed")
            print_info(f"Total validation time: {principles_duration + criteria_duration:.2f} seconds")
            
            self.test_results["performance"] = True
            
        except Exception as e:
            print_error(f"Performance test failed: {e}")
            self.test_results["performance"] = False

def print_final_results(test_results: Dict[str, bool]):
    """Print summary of all test results."""
    print_section("Test Results Summary")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print_info(f"Tests passed: {passed_tests}/{total_tests}")
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    if passed_tests == total_tests:
        print_success("🎉 All design tools tests passed! Tools are ready for Speldesigner agent.")
        print_info("Next steps:")
        print_info("1. Integrate tools with Speldesigner agent")
        print_info("2. Test complete Speldesigner workflow")
        print_info("3. Validate against real feature specifications")
    elif passed_tests >= 4:
        print_info("✨ Core functionality is working!")
        print_info("Most tools passed tests. Review failed tests and fix any issues.")
    else:
        print_error("🚨 Critical issues found. Please fix failing tests before proceeding.")
        print_info("Common solutions:")
        print_info("- Check .env file for correct ANTHROPIC_API_KEY")
        print_info("- Ensure all dependencies are installed")
        print_info("- Verify DNA documents are accessible")

async def main():
    """Main test runner function."""
    print("🚀 Starting DigiNativa Design Tools Test Suite...")
    print_info("This will test all design validation tools for the Speldesigner agent")
    
    try:
        # Initialize test suite
        test_suite = DesignToolsTestSuite()
        
        # Run all tests
        results = await test_suite.run_all_tests()
        
        # Print final results
        print_final_results(results)
        
        # Exit with appropriate code
        passed_tests = sum(1 for result in results.values() if result)
        return passed_tests >= len(results) * 0.8  # 80% pass rate required
        
    except KeyboardInterrupt:
        print_error("\nTests cancelled by user (Ctrl+C)")
        return False
    except Exception as e:
        print_error(f"Test suite failed with unexpected error: {e}")
        return False

# Standalone test function for quick testing
def quick_test():
    """Quick test function that can be run synchronously."""
    print("🧪 Running Quick Design Tools Test...")
    try:
        return test_all_design_tools()
    except Exception as e:
        print_error(f"Quick test failed: {e}")
        return False

if __name__ == "__main__":
    # Run the async test suite
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)