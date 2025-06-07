"""
Architecture Validation Tools for AI Agents
===========================================

PURPOSE:
Provides tools for the Utvecklare agent to validate its own generated code
against the project's strict architectural principles defined in architecture.md.
"""
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tools.file_tools import read_file
import json

class ArchitectureValidationInput(BaseModel):
    """Input for the ArchitectureValidatorTool."""
    file_path: str = Field(..., description="The relative path to the code file to validate.")

class ArchitectureValidatorTool(BaseTool):
    name: str = "Architecture Validator"
    description: str = "Validates a code file against the project's architectural principles (API-first, stateless backend, etc.)."
    args_schema: Type[BaseModel] = ArchitectureValidationInput

    def _run(self, file_path: str) -> str:
        """
        Performs a validation of the code file.
        
        In a real implementation, this would use an LLM to compare the code
        against the rules in 'docs/dna/architecture.md'. For this test,
        we will use a simple heuristic check.
        """
        try:
            code_content = read_file(file_path, agent_name="architecture_validator")
            if code_content.startswith("❌"):
                return json.dumps({"is_compliant": False, "reason": f"Could not read file: {code_content}"})

            is_compliant = True
            reasons = []

            # Simple heuristic checks (to be replaced by LLM logic)
            if "frontend" in file_path:
                if "db" in code_content.lower() or "sql" in code_content.lower():
                    is_compliant = False
                    reasons.append("Potential direct database access from frontend.")
            
            if "backend" in file_path:
                if "session" in code_content.lower():
                    is_compliant = False
                    reasons.append("Potential use of server-side sessions, violating stateless principle.")
            
            if not is_compliant:
                 return json.dumps({"is_compliant": False, "reasons": reasons})

            return json.dumps({
                "is_compliant": True,
                "reasons": ["Code passes basic architectural checks."]
            })

        except Exception as e:
            return json.dumps({"is_compliant": False, "reason": f"An exception occurred during validation: {e}"})
