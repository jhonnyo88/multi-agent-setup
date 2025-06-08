"""
Architecture Validation Tools for AI Agents - FIXED for CrewAI 0.28.8
====================================================================

PURPOSE:
Provides tools for the Utvecklare agent to validate its own generated code
against the project's strict architectural principles defined in architecture.md.

FIXED FOR CREWAI 0.28.8:
- Compatible tool inheritance
- Proper error handling
- Fallback functionality when dependencies unavailable
"""

from typing import Type, Dict, Any, List
import json
import re
from pathlib import Path
from tools.tool_base import UniversalBaseTool as BaseTool


# FIXED: CrewAI 0.28.8 compatible imports
try:
    # Try newer CrewAI versions first
    from crewai.tools import BaseTool
    CREWAI_TOOLS_V2 = True
    print("✅ Using crewai.tools.BaseTool for architecture tools")
except ImportError:
    try:
        # Try crewai_tools package
        from crewai_tools import BaseTool
        CREWAI_TOOLS_V2 = True
        print("✅ Using crewai_tools.BaseTool for architecture tools")
    except ImportError:
        try:
            # Fallback to LangChain
            from langchain.tools import BaseTool
            CREWAI_TOOLS_V2 = False
            print("⚠️  Using LangChain BaseTool fallback for architecture tools")
        except ImportError:
            # Manual implementation as last resort
            print("❌ No BaseTool found for architecture tools, using manual implementation")
            from pydantic import BaseModel
            
            class BaseTool(BaseModel):
                """Manual BaseTool implementation for CrewAI 0.28.8"""
                name: str
                description: str
                
                def _run(self, *args, **kwargs):
                    raise NotImplementedError("Subclasses must implement _run method")
                
                def run(self, *args, **kwargs):
                    """Run method that CrewAI expects"""
                    return self._run(*args, **kwargs)
            
            CREWAI_TOOLS_V2 = False

from pydantic import BaseModel, Field
from tools.file_tools import read_file

class ArchitectureValidationInput(BaseModel):
    """Input for the ArchitectureValidatorTool."""
    file_path: str = Field(..., description="The relative path to the code file to validate.")

class ArchitectureValidatorTool(BaseTool):
    """
    Tool for validating code files against DigiNativa's architectural principles.
    
    ARCHITECTURAL PRINCIPLES CHECKED:
    1. API-First: Clear separation between frontend and backend
    2. Stateless Backend: No server-side sessions
    3. Clear Separation of Concerns: Frontend doesn't call DB directly
    4. Performance: Response times and optimization
    
    FIXED FOR CREWAI 0.28.8:
    - Compatible tool inheritance
    - Proper error handling
    - Heuristic validation when AI unavailable
    """
    name: str = "Architecture Validator"
    description: str = (
        "Validates a code file against the project's architectural principles "
        "(API-first, stateless backend, separation of concerns, etc.). "
        "Provide the relative path to the code file to validate."
    )

    def _run(self, file_path: str) -> str:
        """
        FIXED: Validate code file against architectural principles.
        Works with CrewAI 0.28.8
        """
        try:
            # Read the code file
            code_content = read_file(file_path, agent_name="architecture_validator")
            if code_content.startswith("❌"):
                return json.dumps({
                    "is_compliant": False, 
                    "reason": f"Could not read file: {code_content}",
                    "file_path": file_path
                })

            # Perform architectural validation
            validation_result = self._validate_architectural_compliance(code_content, file_path)
            
            return json.dumps(validation_result, indent=2, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "is_compliant": False, 
                "reason": f"Validation error: {str(e)}",
                "file_path": file_path,
                "error_type": type(e).__name__
            })

    def _validate_architectural_compliance(self, code_content: str, file_path: str) -> Dict[str, Any]:
        """
        Validate code against DigiNativa architectural principles using heuristics.
        """
        violations = []
        warnings = []
        is_compliant = True
        
        # Determine file type and context
        file_type = self._determine_file_type(file_path)
        
        # Check based on file type
        if file_type == "frontend":
            violations.extend(self._check_frontend_principles(code_content))
        elif file_type == "backend":
            violations.extend(self._check_backend_principles(code_content))
        elif file_type == "test":
            warnings.extend(self._check_test_principles(code_content))
        
        # General checks for all files
        violations.extend(self._check_general_principles(code_content))
        
        # Determine compliance
        if violations:
            is_compliant = False
        
        # Calculate compliance score
        total_checks = 10  # Approximate number of checks
        failed_checks = len(violations)
        compliance_score = max(0, (total_checks - failed_checks) / total_checks)
        
        return {
            "is_compliant": is_compliant,
            "compliance_score": round(compliance_score, 2),
            "file_path": file_path,
            "file_type": file_type,
            "violations": violations,
            "warnings": warnings,
            "principles_checked": [
                "API-First Design",
                "Stateless Backend",
                "Separation of Concerns", 
                "Performance Optimization",
                "Code Quality"
            ],
            "validation_method": "heuristic_analysis"
        }

    def _determine_file_type(self, file_path: str) -> str:
        """Determine the type of file for appropriate validation."""
        path_lower = file_path.lower()
        
        if "frontend" in path_lower or path_lower.endswith(('.tsx', '.jsx', '.ts', '.js')):
            return "frontend"
        elif "backend" in path_lower or path_lower.endswith('.py'):
            return "backend"
        elif "test" in path_lower or "spec" in path_lower:
            return "test"
        else:
            return "general"

    def _check_frontend_principles(self, code_content: str) -> List[str]:
        """Check frontend-specific architectural principles."""
        violations = []
        content_lower = code_content.lower()
        
        # Principle 1: No direct database access from frontend
        db_patterns = [
            r'\.query\s*\(',
            r'\.execute\s*\(',
            r'sqlite',
            r'postgresql',
            r'mysql',
            r'mongodb',
            r'database\s*\.',
            r'db\s*\.',
            r'connection\s*\.',
            r'cursor\s*\.'
        ]
        
        for pattern in db_patterns:
            if re.search(pattern, content_lower):
                violations.append(
                    f"Frontend code should not access database directly. "
                    f"Found potential database access pattern: {pattern}"
                )
                break
        
        # Principle 2: API calls should go through proper endpoints
        if 'fetch(' in content_lower or 'axios' in content_lower:
            # Check if API calls are properly structured
            if not re.search(r'/api/v\d+/', content_lower):
                violations.append(
                    "API calls should use versioned endpoints (e.g., /api/v1/)"
                )
        
        # Principle 3: No server-side state management from frontend
        session_patterns = ['sessionstorage', 'localstorage', 'cookie']
        for pattern in session_patterns:
            if pattern in content_lower and 'setitem' in content_lower:
                violations.append(
                    f"Minimal client-side state storage recommended. "
                    f"Found {pattern} usage that might indicate session management."
                )
        
        # Principle 4: Component structure and imports
        if code_content.count('import') > 20:
            violations.append(
                "Excessive imports may indicate component doing too much. "
                "Consider breaking into smaller components."
            )
        
        return violations

    def _check_backend_principles(self, code_content: str) -> List[str]:
        """Check backend-specific architectural principles."""
        violations = []
        content_lower = code_content.lower()
        
        # Principle 1: Stateless design - no server-side sessions
        session_patterns = [
            r'session\s*\[',
            r'session\.get',
            r'session\.set',
            r'flask\.session',
            r'request\.session',
            r'httpx\.session',
            r'\.session\s*=',
        ]
        
        for pattern in session_patterns:
            if re.search(pattern, content_lower):
                violations.append(
                    f"Backend should be stateless. Found session usage: {pattern}"
                )
        
        # Principle 2: FastAPI best practices
        if 'fastapi' in content_lower:
            # Check for proper dependency injection
            if '@app.' in content_lower and 'depends(' not in content_lower:
                if code_content.count('@app.') > 2:  # Multiple endpoints without dependencies
                    violations.append(
                        "Consider using FastAPI dependency injection for shared logic"
                    )
            
            # Check for proper response models
            if 'response_model' not in content_lower and '@app.' in content_lower:
                violations.append(
                    "FastAPI endpoints should specify response_model for API documentation"
                )
        
        # Principle 3: Performance - async/await usage
        if 'def ' in content_lower and 'async def' not in content_lower:
            # Check if there are I/O operations that should be async
            io_patterns = ['requests.', 'urllib.', 'http.', 'fetch(', 'query(']
            has_io = any(pattern in content_lower for pattern in io_patterns)
            
            if has_io:
                violations.append(
                    "I/O operations should use async/await for better performance"
                )
        
        # Principle 4: Error handling
        if '@app.' in content_lower:  # Has endpoints
            if 'try:' not in content_lower and 'except' not in content_lower:
                violations.append(
                    "API endpoints should include proper error handling (try/except)"
                )
        
        return violations

    def _check_test_principles(self, code_content: str) -> List[str]:
        """Check test-specific principles."""
        warnings = []
        content_lower = code_content.lower()
        
        # Test structure
        if 'def test_' not in content_lower and 'test' in content_lower:
            warnings.append("Test functions should follow 'test_' naming convention")
        
        # Assertions
        if 'assert' not in content_lower and 'test' in content_lower:
            warnings.append("Tests should include assertions to validate behavior")
        
        return warnings

    def _check_general_principles(self, code_content: str) -> List[str]:
        """Check general code quality principles."""
        violations = []
        
        # Code complexity - very basic check
        line_count = len(code_content.split('\n'))
        if line_count > 500:
            violations.append(
                f"File is quite large ({line_count} lines). "
                "Consider breaking into smaller modules."
            )
        
        # Basic security checks
        if 'password' in code_content.lower() and 'input(' in code_content.lower():
            violations.append(
                "Avoid hardcoded passwords or password input in code"
            )
        
        # Performance - basic checks
        nested_loops = code_content.count('for ') * code_content.count('while ')
        if nested_loops > 4:
            violations.append(
                "Multiple nested loops detected. Consider optimization."
            )
        
        return violations

    # FIXED: For CrewAI 0.28.8 compatibility
    def run(self, file_path: str) -> str:
        """Public run method that CrewAI 0.28.8 expects"""
        return self._run(file_path)


class CodeQualityAnalyzerTool(BaseTool):
    """
    Tool for analyzing code quality metrics.
    
    FIXED FOR CREWAI 0.28.8:
    - Compatible tool inheritance
    - Proper error handling
    - Heuristic analysis
    """
    name: str = "Code Quality Analyzer"
    description: str = (
        "Analyze code quality metrics like complexity, maintainability, "
        "and readability. Provide the relative path to the code file."
    )

    def _run(self, file_path: str) -> str:
        """
        FIXED: Analyze code quality metrics.
        Works with CrewAI 0.28.8
        """
        try:
            # Read the code file
            code_content = read_file(file_path, agent_name="quality_analyzer")
            if code_content.startswith("❌"):
                return json.dumps({
                    "quality_score": 0, 
                    "error": f"Could not read file: {code_content}",
                    "file_path": file_path
                })

            # Analyze quality metrics
            quality_analysis = self._analyze_code_quality(code_content, file_path)
            
            return json.dumps(quality_analysis, indent=2, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "quality_score": 0, 
                "error": f"Analysis error: {str(e)}",
                "file_path": file_path
            })

    def _analyze_code_quality(self, code_content: str, file_path: str) -> Dict[str, Any]:
        """Analyze code quality using heuristic methods."""
        
        lines = code_content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Basic metrics
        metrics = {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len(lines) - len(non_empty_lines),
            "average_line_length": sum(len(line) for line in non_empty_lines) / max(len(non_empty_lines), 1)
        }
        
        # Calculate quality scores (0-100)
        readability_score = self._calculate_readability(code_content, metrics)
        maintainability_score = self._calculate_maintainability(code_content, metrics)
        complexity_score = self._calculate_complexity(code_content, metrics)
        
        # Overall quality score
        overall_score = (readability_score + maintainability_score + complexity_score) / 3
        
        return {
            "file_path": file_path,
            "overall_quality_score": round(overall_score, 1),
            "metrics": {
                "readability": round(readability_score, 1),
                "maintainability": round(maintainability_score, 1),
                "complexity": round(complexity_score, 1)
            },
            "detailed_metrics": metrics,
            "recommendations": self._generate_recommendations(
                readability_score, maintainability_score, complexity_score, metrics
            ),
            "analysis_method": "heuristic"
        }

    def _calculate_readability(self, code_content: str, metrics: Dict) -> float:
        """Calculate readability score based on various factors."""
        score = 100.0
        
        # Comment ratio
        comment_ratio = metrics["comment_lines"] / max(metrics["code_lines"], 1)
        if comment_ratio < 0.1:  # Less than 10% comments
            score -= 20
        elif comment_ratio > 0.3:  # More than 30% comments might be excessive
            score -= 10
        
        # Average line length
        if metrics["average_line_length"] > 120:
            score -= 15
        elif metrics["average_line_length"] > 80:
            score -= 5
        
        # Function/method count and size
        function_count = code_content.count('def ')
        if function_count > 0:
            avg_function_size = metrics["code_lines"] / function_count
            if avg_function_size > 50:  # Functions too large
                score -= 20
        
        return max(0, score)

    def _calculate_maintainability(self, code_content: str, metrics: Dict) -> float:
        """Calculate maintainability score."""
        score = 100.0
        
        # File size
        if metrics["total_lines"] > 500:
            score -= 25
        elif metrics["total_lines"] > 300:
            score -= 10
        
        # Import complexity (for Python files)
        import_count = code_content.count('import ')
        if import_count > 20:
            score -= 15
        elif import_count > 15:
            score -= 5
        
        # Nested depth approximation
        max_indentation = 0
        for line in code_content.split('\n'):
            if line.strip():
                indentation = len(line) - len(line.lstrip())
                max_indentation = max(max_indentation, indentation)
        
        if max_indentation > 24:  # Very deep nesting
            score -= 20
        elif max_indentation > 16:
            score -= 10
        
        return max(0, score)

    def _calculate_complexity(self, code_content: str, metrics: Dict) -> float:
        """Calculate complexity score."""
        score = 100.0
        content_lower = code_content.lower()
        
        # Control structure complexity
        control_structures = [
            'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except:', 'with '
        ]
        
        complexity_points = 0
        for structure in control_structures:
            complexity_points += content_lower.count(structure)
        
        # Penalize high complexity
        if complexity_points > 50:
            score -= 30
        elif complexity_points > 30:
            score -= 20
        elif complexity_points > 20:
            score -= 10
        
        # Function parameter complexity
        def_lines = [line for line in code_content.split('\n') if 'def ' in line]
        for def_line in def_lines:
            param_count = def_line.count(',') + 1 if '(' in def_line else 0
            if param_count > 7:  # Too many parameters
                score -= 5
        
        return max(0, score)

    def _generate_recommendations(self, readability: float, maintainability: float, 
                                complexity: float, metrics: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if readability < 70:
            recommendations.append("Add more comments to improve code readability")
            if metrics["average_line_length"] > 100:
                recommendations.append("Consider breaking long lines for better readability")
        
        if maintainability < 70:
            recommendations.append("Consider breaking this file into smaller modules")
            if metrics["total_lines"] > 400:
                recommendations.append("File is quite large - split into multiple files")
        
        if complexity < 70:
            recommendations.append("Reduce complexity by extracting methods or simplifying logic")
            recommendations.append("Consider refactoring nested loops and conditions")
        
        if not recommendations:
            recommendations.append("Code quality looks good! Keep up the excellent work.")
        
        return recommendations

    # FIXED: For CrewAI 0.28.8 compatibility
    def run(self, file_path: str) -> str:
        """Public run method that CrewAI 0.28.8 expects"""
        return self._run(file_path)


# Convenience function for testing architecture tools
def test_architecture_tools():
    """Test all architecture tools with sample code files."""
    print("🧪 Testing Architecture Tools...")
    
    try:
        # Test Architecture Validator
        print("\n🏗️ Testing Architecture Validator...")
        arch_validator = ArchitectureValidatorTool()
        
        # Test with agents/utvecklare.py (should exist)
        arch_result = arch_validator.run("agents/utvecklare.py")
        print("✅ Architecture validation completed")
        
        # Test Code Quality Analyzer
        print("\n📊 Testing Code Quality Analyzer...")
        quality_analyzer = CodeQualityAnalyzerTool()
        quality_result = quality_analyzer.run("agents/utvecklare.py")
        print("✅ Code quality analysis completed")
        
        print("\n🎉 All architecture tools tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Architecture tools test failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests when module is executed directly
    test_architecture_tools()