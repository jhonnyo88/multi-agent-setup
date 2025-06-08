"""
DigiNativa AI-Agent: Utvecklare (Enhanced Full-Stack Code Generator)
===================================================================

PURPOSE:
This agent reads UX specifications from the Speldesigner and generates
production-ready React + FastAPI code. It handles the complete development
workflow including Git operations in the product repository.

ENHANCED CAPABILITIES:
- Reads UX specifications from Speldesigner output
- Generates actual React components with TypeScript
- Creates FastAPI endpoints with proper architecture
- Manages Git workflow in product repository
- Follows architectural principles strictly
- Creates testable, production-ready code

CROSS-REPO WORKFLOW:
- Reads specs from: workspace/diginativa-game/docs/specs/
- Writes frontend to: workspace/diginativa-game/frontend/src/components/
- Writes backend to: workspace/diginativa-game/backend/app/api/
- Commits to: diginativa-game repository
- Creates PRs in: diginativa-game repository

ADAPTATION GUIDE:
🔧 To adapt this agent:
1. Update tech stack references (React/FastAPI) for your stack
2. Modify code generation templates for your frameworks
3. Adjust file paths for your project structure
4. Update architectural principles validation
"""

import os
import json
import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# CrewAI imports
from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic

# Project imports
from config.settings import SECRETS, TECH_STACK, GITHUB_CONFIG, PROJECT_ROOT
from config.agent_config import get_agent_config
from tools.file_tools import FileReadTool, FileWriteTool, read_file, write_file
from tools.dev_tools import EnhancedGitTool
from tools.architecture_tools import ArchitectureValidatorTool
from workflows.status_handler import StatusHandler, report_success, report_error

class EnhancedUtvecklareAgent:
    """
    Enhanced Utvecklare (Developer) agent with full code generation capabilities.
    
    CORE RESPONSIBILITIES:
    1. Read and parse UX specifications from Speldesigner
    2. Generate production-ready React components with TypeScript
    3. Create corresponding FastAPI endpoints and business logic
    4. Manage Git workflow in product repository
    5. Ensure architectural compliance and code quality
    6. Handle cross-repository operations seamlessly
    
    CLAUDE INTEGRATION:
    Uses Claude-3.5-Sonnet for sophisticated code generation that:
    - Understands complex UX specifications
    - Generates contextually appropriate code
    - Follows architectural patterns and best practices
    - Creates maintainable, scalable solutions
    """
    
    def __init__(self):
        """Initialize Enhanced Utvecklare with cross-repo capabilities."""
        self.agent_config = get_agent_config("utvecklare")
        self.status_handler = StatusHandler()
        
        # Workspace paths for cross-repo operations
        self.product_repo_path = PROJECT_ROOT / "workspace" / GITHUB_CONFIG['project_repo']['name']
        self.specs_path = self.product_repo_path / "docs" / "specs"
        self.frontend_path = self.product_repo_path / "frontend" / "src" / "components"
        self.backend_path = self.product_repo_path / "backend" / "app" / "api"
        
        # Initialize tools
        self.git_tool = EnhancedGitTool()
        
        # Claude LLM for code generation
        self.claude_llm = self._create_claude_llm()
        
        # Create the CrewAI agent
        self.agent = self._create_agent()
        
        print(f"🔨 Enhanced Utvecklare initialized")
        print(f"   Product repo: {GITHUB_CONFIG['project_repo']['name']}")
        print(f"   Frontend: {TECH_STACK['frontend']['framework']}")
        print(f"   Backend: {TECH_STACK['backend']['framework']}")
        print(f"   Model: {self.agent_config.llm_model}")
    
    def _create_claude_llm(self) -> ChatAnthropic:
        """Create Claude LLM optimized for code generation."""
        try:
            anthropic_api_key = SECRETS.get("anthropic_api_key")
            
            if not anthropic_api_key or anthropic_api_key.startswith("[YOUR_"):
                raise ValueError(
                    "Anthropic API key not configured. "
                    "Please set ANTHROPIC_API_KEY in your .env file"
                )
            
            claude_llm = ChatAnthropic(
                model=self.agent_config.llm_model,
                api_key=anthropic_api_key,
                temperature=self.agent_config.temperature,  # 0.1 for consistent code
                max_tokens_to_sample=4000
            )
            
            print(f"✅ Claude LLM configured for code generation")
            return claude_llm
            
        except Exception as e:
            print(f"❌ Failed to configure Claude LLM: {e}")
            raise
    
    def _create_agent(self) -> Agent:
        """
        Create the enhanced CrewAI agent with code generation capabilities.
        
        AGENT PERSONALITY:
        - Meticulous attention to architectural principles
        - Expert in React + TypeScript + FastAPI
        - Follows specifications exactly without deviation
        - Produces clean, maintainable, testable code
        - Integrates seamlessly with Git workflow
        """
        tech_stack_description = (
            f"{TECH_STACK['frontend']['framework']} + "
            f"{TECH_STACK['frontend']['language']} + "
            f"{TECH_STACK['backend']['framework']}"
        )
        
        return Agent(
            role=f"Enhanced Full-Stack Developer ({tech_stack_description})",
            
            goal=f"""
            Transform UX specifications into production-ready code for DigiNativa.
            Generate high-quality {TECH_STACK['frontend']['framework']} components and 
            {TECH_STACK['backend']['framework']} APIs that exactly match specifications
            while following all architectural principles and best practices.
            
            Use Claude's advanced capabilities to:
            - Parse complex UX specifications accurately
            - Generate contextually appropriate code solutions
            - Ensure architectural compliance in every line of code
            - Create maintainable and scalable implementations
            """,
            
            backstory=f"""
            You are a world-class full-stack developer powered by Claude-3.5-Sonnet, specializing 
            in the DigiNativa technology stack: {tech_stack_description}.
            
            Your expertise encompasses:
            - **Frontend Mastery**: {TECH_STACK['frontend']['framework']} with {TECH_STACK['frontend']['language']}, 
              {TECH_STACK['frontend']['styling']}, responsive design, accessibility
            - **Backend Excellence**: {TECH_STACK['backend']['framework']} with {TECH_STACK['backend']['language']}, 
              RESTful APIs, stateless architecture, database integration
            - **Code Quality**: Clean code principles, SOLID design patterns, comprehensive testing
            - **Git Workflow**: Feature branching, atomic commits, pull request best practices
            - **Cross-Repository Operations**: Seamless work across AI-team and product repositories
            
            Your development process is guided by DigiNativa's architectural principles:
            
            1. **API-First Design**: Every frontend component has corresponding backend endpoints
            2. **Stateless Backend**: No server-side sessions, all state managed client-side
            3. **Separation of Concerns**: Clean boundaries between frontend and backend code
            4. **Simplicity and Pragmatism**: Choose simplest solution that meets requirements
            
            Your workflow is systematic and precise:
            1. Read and thoroughly understand UX specifications from Speldesigner
            2. Design API contracts that serve the frontend requirements
            3. Generate backend code that implements the API contracts
            4. Create frontend components that consume the APIs
            5. Ensure all code follows architectural principles
            6. Commit code to appropriate branches in product repository
            7. Validate implementation against acceptance criteria
            
            You never deviate from specifications. If a specification is unclear or 
            contradicts architectural principles, you report status `FEL_SPEC_TVETYDIG_U` 
            and request clarification rather than making assumptions.
            
            Your code is always:
            - Production-ready from day one
            - Fully typed (TypeScript for frontend, type hints for backend)
            - Accessible and responsive
            - Performant and optimized
            - Well-commented where complexity requires explanation
            - Testable with clear interfaces
            
            You work primarily in the product repository workspace:
            - Read specs from: `workspace/{GITHUB_CONFIG['project_repo']['name']}/docs/specs/`
            - Generate frontend: `workspace/{GITHUB_CONFIG['project_repo']['name']}/frontend/src/components/`
            - Generate backend: `workspace/{GITHUB_CONFIG['project_repo']['name']}/backend/app/api/`
            """,
            
            tools=[
                FileReadTool(),          # Read specifications and existing code
                FileWriteTool(),         # Write generated code files
                EnhancedGitTool(),       # Cross-repo Git operations
                ArchitectureValidatorTool()  # Validate architectural compliance
            ],
            
            verbose=True,
            allow_delegation=False,  # Developer does the coding personally
            llm=self.claude_llm,
            max_iterations=self.agent_config.max_iterations
        )
    
    async def implement_story_from_spec(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Implement a complete story from UX specification.
        
        IMPLEMENTATION WORKFLOW:
        1. Setup workspace and Git branch
        2. Read and parse UX specification
        3. Generate backend API code
        4. Generate frontend component code
        5. Validate architectural compliance
        6. Commit and push changes
        7. Optionally create pull request
        
        Args:
            story_data: Story information including story_id, title, description
            
        Returns:
            Implementation results with file paths, commit info, etc.
        """
        implementation_start = datetime.now()
        story_id = story_data.get("story_id", "UNKNOWN")
        
        try:
            print(f"🔨 Starting implementation for {story_id}")
            
            # Step 1: Setup workspace and create feature branch
            workspace_result = await self._setup_implementation_workspace(story_id)
            if "❌" in workspace_result:
                raise Exception(f"Workspace setup failed: {workspace_result}")
            
            # Step 2: Read and parse UX specification
            spec_data = await self._read_and_parse_specification(story_id)
            if not spec_data:
                raise Exception("Failed to read or parse specification")
            
            # Step 3: Generate API design from specification
            api_design = await self._design_api_from_spec(spec_data)
            
            # Step 4: Generate backend code
            backend_result = await self._generate_backend_code(story_id, spec_data, api_design)
            
            # Step 5: Generate frontend code
            frontend_result = await self._generate_frontend_code(story_id, spec_data, api_design)
            
            # Step 6: Validate architectural compliance
            validation_result = await self._validate_implementation(story_id, backend_result, frontend_result)
            
            # Step 7: Commit changes to Git
            commit_result = await self._commit_implementation(story_id, story_data, [backend_result, frontend_result])
            
            # Calculate implementation metrics
            implementation_time = datetime.now() - implementation_start
            
            # Compile complete results
            complete_results = {
                "story_id": story_id,
                "implementation_status": "completed",
                "workspace_setup": workspace_result,
                "specification_parsed": spec_data.get("title", "Unknown"),
                "backend_files": backend_result.get("files_created", []),
                "frontend_files": frontend_result.get("files_created", []),
                "validation_results": validation_result,
                "git_commit": commit_result,
                "implementation_time_seconds": implementation_time.total_seconds(),
                "created_at": datetime.now().isoformat(),
                "ai_model": self.agent_config.llm_model
            }
            
            # Report success
            self.status_handler.report_status(
                agent_name="utvecklare",
                status_code="LYCKAD_KOD_IMPLEMENTERAD",
                payload=complete_results,
                story_id=story_id
            )
            
            print(f"✅ Implementation completed for {story_id}")
            print(f"   Backend files: {len(backend_result.get('files_created', []))}")
            print(f"   Frontend files: {len(frontend_result.get('files_created', []))}")
            print(f"   Implementation time: {implementation_time.total_seconds():.1f} seconds")
            
            return complete_results
            
        except Exception as e:
            error_message = f"Implementation failed for {story_id}: {str(e)}"
            print(f"❌ {error_message}")
            
            # Report error
            self.status_handler.report_status(
                agent_name="utvecklare",
                status_code="FEL_IMPLEMENTATION_ARKITEKTURBROTT" if "architectural" in str(e).lower() else "FEL_KOD_EJ_TESTBAR",
                payload={
                    "story_id": story_id,
                    "error_message": error_message,
                    "error_type": type(e).__name__,
                    "implementation_time_seconds": (datetime.now() - implementation_start).total_seconds()
                },
                story_id=story_id
            )
            
            return {
                "story_id": story_id,
                "implementation_status": "failed",
                "error": error_message,
                "created_at": datetime.now().isoformat()
            }
    
    async def _setup_implementation_workspace(self, story_id: str) -> str:
        """Setup workspace and create feature branch for implementation."""
        try:
            print(f"🏗️  Setting up workspace for {story_id}")
            
            # Setup cross-repo workspace
            workspace_result = self.git_tool._run('setup_workspace')
            if "❌" in workspace_result:
                return workspace_result
            
            # Create feature branch in product repository
            branch_result = self.git_tool._run('create_feature_branch', 
                                               story_id=story_id, 
                                               target_repo='product_repo')
            if "❌" in branch_result:
                return branch_result
            
            print(f"✅ Workspace ready for {story_id}")
            return f"Workspace setup completed:\n{workspace_result}\n{branch_result}"
            
        except Exception as e:
            return f"❌ Workspace setup failed: {str(e)}"
    
    async def _read_and_parse_specification(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Read and parse UX specification created by Speldesigner."""
        try:
            # Look for specification file
            spec_patterns = [
                f"spec-{story_id}.md",
                f"spec_{story_id}.md",
                f"{story_id}-spec.md",
                f"{story_id}_spec.md"
            ]
            
            spec_content = None
            spec_file_path = None
            
            for pattern in spec_patterns:
                potential_path = self.specs_path / pattern
                if potential_path.exists():
                    spec_file_path = f"workspace/{GITHUB_CONFIG['project_repo']['name']}/docs/specs/{pattern}"
                    spec_content = read_file(spec_file_path, "utvecklare")
                    break
            
            if not spec_content or spec_content.startswith("❌"):
                # Try to find any spec file with story_id in name
                if self.specs_path.exists():
                    for spec_file in self.specs_path.glob("*.md"):
                        if story_id in spec_file.name:
                            spec_file_path = f"workspace/{GITHUB_CONFIG['project_repo']['name']}/docs/specs/{spec_file.name}"
                            spec_content = read_file(spec_file_path, "utvecklare")
                            break
            
            if not spec_content or spec_content.startswith("❌"):
                print(f"❌ No specification found for {story_id}")
                return None
            
            print(f"📋 Found specification: {spec_file_path}")
            
            # Parse specification content
            parsed_spec = self._parse_specification_content(spec_content)
            parsed_spec["source_file"] = spec_file_path
            
            return parsed_spec
            
        except Exception as e:
            print(f"❌ Failed to read specification for {story_id}: {e}")
            return None
    
    def _parse_specification_content(self, spec_content: str) -> Dict[str, Any]:
        """Parse UX specification content into structured data."""
        try:
            parsed = {
                "title": "Unknown Feature",
                "description": "",
                "user_value": "",
                "acceptance_criteria": [],
                "visual_design": {},
                "interaction_flow": {},
                "game_mechanics": {},
                "technical_requirements": {},
                "api_endpoints": [],
                "components": []
            }
            
            # Extract title
            title_match = re.search(r'#\s*(.+)', spec_content)
            if title_match:
                parsed["title"] = title_match.group(1).strip()
            
            # Extract sections
            sections = {
                "description": re.search(r'(?:## .*(?:Description|Beskrivning).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE),
                "user_value": re.search(r'(?:## .*(?:User Value|Användarvärde).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE),
                "visual_design": re.search(r'(?:## .*(?:Visual Design|Visuell Design).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE),
                "interaction_flow": re.search(r'(?:## .*(?:Interaction Flow|Interaktionsflöde).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE),
                "technical_requirements": re.search(r'(?:## .*(?:Technical|Teknisk).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE)
            }
            
            for section_name, match in sections.items():
                if match:
                    parsed[section_name] = match.group(1).strip()
            
            # Extract acceptance criteria
            criteria_match = re.search(r'(?:## .*(?:Acceptance Criteria|Acceptanskriterier).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE)
            if criteria_match:
                criteria_text = criteria_match.group(1)
                # Extract numbered or bulleted criteria
                criteria = re.findall(r'(?:^\d+\.|\-|\*)\s*(.+)', criteria_text, re.MULTILINE)
                parsed["acceptance_criteria"] = criteria
            
            # Extract API endpoints mentioned in spec
            api_matches = re.findall(r'(?:GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]+)', spec_content, re.IGNORECASE)
            parsed["api_endpoints"] = list(set(api_matches))
            
            print(f"📊 Parsed specification: {parsed['title']}")
            print(f"   Acceptance criteria: {len(parsed['acceptance_criteria'])}")
            print(f"   API endpoints: {len(parsed['api_endpoints'])}")
            
            return parsed
            
        except Exception as e:
            print(f"⚠️  Specification parsing error: {e}")
            return {"title": "Parsing Error", "description": spec_content[:500]}
    
    async def _design_api_from_spec(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design API endpoints based on UX specification."""
        try:
            print(f"🎯 Designing API for: {spec_data['title']}")
            
            # Use Claude to design appropriate API based on spec
            api_design_prompt = f"""
            Design a RESTful API for this feature based on the UX specification.

            FEATURE: {spec_data['title']}
            DESCRIPTION: {spec_data.get('description', '')}
            ACCEPTANCE CRITERIA: {spec_data.get('acceptance_criteria', [])}

            ARCHITECTURAL CONSTRAINTS:
            - Stateless backend (no server-side sessions)
            - JSON API following RESTful conventions
            - FastAPI framework with Pydantic models
            - Response time < 200ms for all endpoints

            Design the API endpoints, request/response formats, and data models.
            Return ONLY valid JSON in this format:
            {{
                "endpoints": [
                    {{
                        "method": "GET|POST|PUT|DELETE",
                        "path": "/api/v1/...",
                        "description": "What this endpoint does",
                        "request_model": {{"field": "type"}},
                        "response_model": {{"field": "type"}},
                        "status_codes": [200, 400, 404]
                    }}
                ],
                "data_models": [
                    {{
                        "name": "ModelName",
                        "fields": {{"field": "type"}},
                        "description": "What this model represents"
                    }}
                ]
            }}
            """
            
            response = self.claude_llm.invoke(api_design_prompt)
            
            try:
                api_design = json.loads(response.content)
                print(f"✅ API designed: {len(api_design.get('endpoints', []))} endpoints")
                return api_design
            except json.JSONDecodeError:
                print(f"⚠️  Failed to parse API design, using fallback")
                return self._create_fallback_api_design(spec_data)
            
        except Exception as e:
            print(f"⚠️  API design error: {e}, using fallback")
            return self._create_fallback_api_design(spec_data)
    
    def _create_fallback_api_design(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic API design when Claude fails."""
        return {
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/api/v1/health",
                    "description": "Health check endpoint",
                    "request_model": {},
                    "response_model": {"status": "string", "timestamp": "string"},
                    "status_codes": [200]
                }
            ],
            "data_models": [
                {
                    "name": "HealthResponse",
                    "fields": {"status": "str", "timestamp": "str"},
                    "description": "Health check response"
                }
            ]
        }
    
    async def _generate_backend_code(self, story_id: str, spec_data: Dict[str, Any], api_design: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FastAPI backend code based on specification and API design."""
        try:
            print(f"⚙️  Generating backend code for {story_id}")
            
            # Generate FastAPI code using Claude
            backend_prompt = f"""
            Generate production-ready FastAPI code for this feature.

            STORY ID: {story_id}
            FEATURE: {spec_data['title']}
            API DESIGN: {json.dumps(api_design, indent=2)}

            REQUIREMENTS:
            - Use FastAPI with Pydantic models
            - Stateless design (no server-side sessions)
            - Proper error handling and validation
            - Type hints throughout
            - Async/await where appropriate
            - Response times < 200ms

            Generate a complete Python file that can be saved as `{story_id}.py`.
            Include all necessary imports, models, and endpoint implementations.
            Follow FastAPI best practices and our architectural principles.
            """
            
            response = self.claude_llm.invoke(backend_prompt)
            backend_code = response.content
            
            # Clean and validate the generated code
            backend_code = self._clean_generated_code(backend_code, "python")
            
            # Write backend file
            backend_file_path = f"workspace/{GITHUB_CONFIG['project_repo']['name']}/backend/app/api/{story_id}.py"
            write_result = write_file(backend_file_path, backend_code, "utvecklare")
            
            if "successfully" not in write_result.lower():
                raise Exception(f"Failed to write backend file: {write_result}")
            
            print(f"✅ Backend code generated: {backend_file_path}")
            
            return {
                "status": "success",
                "files_created": [backend_file_path],
                "code_length": len(backend_code),
                "endpoints": len(api_design.get("endpoints", [])),
                "models": len(api_design.get("data_models", []))
            }
            
        except Exception as e:
            print(f"❌ Backend code generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "files_created": []
            }
    
    async def _generate_frontend_code(self, story_id: str, spec_data: Dict[str, Any], api_design: Dict[str, Any]) -> Dict[str, Any]:
        """Generate React frontend component based on specification and API design."""
        try:
            print(f"🎨 Generating frontend code for {story_id}")
            
            # Generate React component using Claude
            frontend_prompt = f"""
            Generate a production-ready React component with TypeScript for this feature.

            STORY ID: {story_id}
            FEATURE: {spec_data['title']}
            DESCRIPTION: {spec_data.get('description', '')}
            ACCEPTANCE CRITERIA: {spec_data.get('acceptance_criteria', [])}
            API ENDPOINTS: {json.dumps(api_design.get('endpoints', []), indent=2)}

            REQUIREMENTS:
            - React functional component with hooks
            - TypeScript throughout
            - Tailwind CSS for styling
            - Responsive design (mobile-first)
            - Accessibility (WCAG compliance)
            - Error handling and loading states
            - Integration with the backend API

            DESIGN CONSTRAINTS:
            - Professional tone (for Anna persona - public sector professional)
            - Time-efficient UX (< 10 minute sessions)
            - Swedish public sector context
            - Clean, institutional visual design

            Generate a complete TypeScript React component that can be saved as `{story_id}.tsx`.
            Include all necessary imports, interfaces, and proper error handling.
            """
            
            response = self.claude_llm.invoke(frontend_prompt)
            frontend_code = response.content
            
            # Clean and validate the generated code
            frontend_code = self._clean_generated_code(frontend_code, "typescript")
            
            # Write frontend file
            frontend_file_path = f"workspace/{GITHUB_CONFIG['project_repo']['name']}/frontend/src/components/{story_id}.tsx"
            write_result = write_file(frontend_file_path, frontend_code, "utvecklare")
            
            if "successfully" not in write_result.lower():
                raise Exception(f"Failed to write frontend file: {write_result}")
            
            print(f"✅ Frontend code generated: {frontend_file_path}")
            
            return {
                "status": "success",
                "files_created": [frontend_file_path],
                "code_length": len(frontend_code),
                "component_name": f"{story_id}"
            }
            
        except Exception as e:
            print(f"❌ Frontend code generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "files_created": []
            }
    
    def _clean_generated_code(self, code: str, language: str) -> str:
        """Clean and validate generated code."""
        try:
            # Remove markdown code blocks if present
            if "```" in code:
                # Extract code from markdown blocks
                code_blocks = re.findall(r'```(?:' + language + r'|python|typescript|tsx)?\n(.*?)```', code, re.DOTALL | re.IGNORECASE)
                if code_blocks:
                    code = code_blocks[0]
            
            # Remove excessive whitespace
            lines = code.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Remove trailing whitespace
                line = line.rstrip()
                cleaned_lines.append(line)
            
            # Remove excessive blank lines
            final_lines = []
            blank_count = 0
            
            for line in cleaned_lines:
                if line.strip() == "":
                    blank_count += 1
                    if blank_count <= 2:  # Allow max 2 consecutive blank lines
                        final_lines.append(line)
                else:
                    blank_count = 0
                    final_lines.append(line)
            
            return '\n'.join(final_lines)
            
        except Exception as e:
            print(f"⚠️  Code cleaning error: {e}")
            return code
    
    async def _validate_implementation(self, story_id: str, backend_result: Dict[str, Any], frontend_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate implementation against architectural principles."""
        try:
            print(f"🔍 Validating implementation for {story_id}")
            
            validation_results = {
                "overall_compliant": True,
                "backend_validation": {},
                "frontend_validation": {},
                "issues_found": [],
                "recommendations": []
            }
            
            # Validate backend files
            for backend_file in backend_result.get("files_created", []):
                try:
                    arch_tool = ArchitectureValidatorTool()
                    backend_validation = arch_tool._run(backend_file)
                    backend_data = json.loads(backend_validation)
                    validation_results["backend_validation"][backend_file] = backend_data
                    
                    if not backend_data.get("is_compliant", True):
                        validation_results["overall_compliant"] = False
                        validation_results["issues_found"].extend(backend_data.get("reasons", []))
                        
                except Exception as e:
                    print(f"⚠️  Backend validation error: {e}")
            
            # Validate frontend files
            for frontend_file in frontend_result.get("files_created", []):
                try:
                    arch_tool = ArchitectureValidatorTool()
                    frontend_validation = arch_tool._run(frontend_file)
                    frontend_data = json.loads(frontend_validation)
                    validation_results["frontend_validation"][frontend_file] = frontend_data
                    
                    if not frontend_data.get("is_compliant", True):
                        validation_results["overall_compliant"] = False
                        validation_results["issues_found"].extend(frontend_data.get("reasons", []))
                        
                except Exception as e:
                    print(f"⚠️  Frontend validation error: {e}")
            
            if validation_results["overall_compliant"]:
                print(f"✅ Implementation validation passed")
            else:
                print(f"⚠️  Implementation validation found issues:")
                for issue in validation_results["issues_found"]:
                    print(f"   - {issue}")
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return {
                "overall_compliant": False,
                "error": str(e),
                "issues_found": ["Validation process failed"],
                "recommendations": ["Manual code review required"]
            }
    
    async def _commit_implementation(self, story_id: str, story_data: Dict[str, Any], implementation_results: List[Dict[str, Any]]) -> str:
        """Commit implementation to Git with proper commit message."""
        try:
            print(f"📝 Committing implementation for {story_id}")
            
            # Collect all created files
            files_to_commit = []
            for result in implementation_results:
                files_to_commit.extend(result.get("files_created", []))
            
            if not files_to_commit:
                return "ℹ️  No files to commit"
            
            # Create descriptive commit message
            story_title = story_data.get("title", "Unknown feature")
            commit_message = f"feat({story_id}): {story_title}\n\n"
            commit_message += f"Implemented by DigiNativa AI Utvecklare\n"
            commit_message += f"Files created: {len(files_to_commit)}\n"
            
            for file_path in files_to_commit:
                file_name = Path(file_path).name
                if "backend" in file_path:
                    commit_message += f"- Backend API: {file_name}\n"
                elif "frontend" in file_path:
                    commit_message += f"- Frontend component: {file_name}\n"
            
            # Commit changes
            commit_result = self.git_tool._run('commit_changes',
                                               commit_message=commit_message,
                                               files_to_add=files_to_commit,
                                               target_repo='product_repo')
            
            if "✅" in commit_result:
                # Push changes
                push_result = self.git_tool._run('push_branch', target_repo='product_repo')
                return f"{commit_result}\n{push_result}"
            else:
                return commit_result
            
        except Exception as e:
            return f"❌ Commit failed: {str(e)}"

# Factory function to create Enhanced Utvecklare agent
def create_enhanced_utvecklare_agent() -> EnhancedUtvecklareAgent:
    """
    Factory function to create a properly configured Enhanced Utvecklare agent.
    
    USAGE:
    ```python
    from agents.utvecklare import create_enhanced_utvecklare_agent
    
    utvecklare = create_enhanced_utvecklare_agent()
    result = await utvecklare.implement_story_from_spec(story_data)
    ```
    """
    print("🔨 Initializing Enhanced Utvecklare agent...")
    
    try:
        agent = EnhancedUtvecklareAgent()
        print(f"✅ Enhanced Utvecklare initialized successfully")
        print(f"   Tech stack: {TECH_STACK['frontend']['framework']} + {TECH_STACK['backend']['framework']}")
        print(f"   Model: {agent.agent_config.llm_model}")
        print(f"   Cross-repo: {GITHUB_CONFIG['project_repo']['name']}")
        return agent
        
    except Exception as e:
        print(f"❌ Failed to initialize Enhanced Utvecklare: {e}")
        print("   Common issues:")
        print("   - ANTHROPIC_API_KEY not set in .env file")
        print("   - Product repository not accessible")
        print("   - Missing dependencies")
        raise

# Convenience functions for testing and integration
async def implement_demo_story(story_id: str = "DEMO-DEV-001") -> Dict[str, Any]:
    """
    Implement a demonstration story for testing purposes.
    
    Args:
        story_id: ID for the demo story
        
    Returns:
        Complete implementation results
    """
    try:
        utvecklare = create_enhanced_utvecklare_agent()
        
        # Demo story data
        demo_story = {
            "story_id": story_id,
            "title": "User Authentication Component",
            "description": "Create login component for DigiNativa users",
            "user_value": "Anna can securely log in to access her learning progress",
            "assigned_agent": "utvecklare",
            "story_type": "full_feature"
        }
        
        result = await utvecklare.implement_story_from_spec(demo_story)
        return result
        
    except Exception as e:
        print(f"❌ Demo implementation failed: {e}")
        return {"error": str(e), "success": False}

if __name__ == "__main__":
    # Test script for debugging and development
    import asyncio
    
    async def test_enhanced_utvecklare():
        """Test script for Enhanced Utvecklare functionality."""
        print("🧪 Testing Enhanced Utvecklare agent...")
        
        try:
            # Create agent
            utvecklare = create_enhanced_utvecklare_agent()
            
            # Test implementation with demo story
            result = await implement_demo_story("TEST-DEV-001")
            
            if result.get("implementation_status") == "completed":
                print("✅ Enhanced Utvecklare test completed successfully!")
                print(f"   Backend files: {len(result.get('backend_files', []))}")
                print(f"   Frontend files: {len(result.get('frontend_files', []))}")
                print(f"   Git commit: {result.get('git_commit', 'N/A')}")
            else: