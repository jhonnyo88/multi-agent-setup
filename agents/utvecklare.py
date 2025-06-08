"""
DigiNativa AI-Agent: Utvecklare (Enhanced Full-Stack Code Generator) - FIXED
===========================================================================

PURPOSE:
This agent reads UX specifications from the Speldesigner and generates
production-ready React + FastAPI code. Enhanced with proper CrewAI compatibility.

FIXED ISSUES:
- CrewAI tool compatibility 
- Import fixes for different versions
- Proper error handling
- Git workflow integration
"""

import os
import json
import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Fixed CrewAI imports
try:
    from crewai import Agent, Task, Crew
    from langchain_anthropic import ChatAnthropic
    CREWAI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  CrewAI import issue: {e}")
    CREWAI_AVAILABLE = False
    # Create dummy classes for development
    class Agent: pass
    class Task: pass  
    class Crew: pass
    class ChatAnthropic: pass

# Project imports
from config.settings import SECRETS, TECH_STACK, GITHUB_CONFIG, PROJECT_ROOT
from config.agent_config import get_agent_config
from tools.file_tools import FileReadTool, FileWriteTool, read_file, write_file
from workflows.status_handler import StatusHandler

class EnhancedUtvecklareAgent:
    """
    Enhanced Utvecklare (Developer) agent with full code generation capabilities.
    
    FIXED FEATURES:
    - CrewAI compatibility across versions
    - Robust error handling
    - Cross-repository Git operations
    - Production-ready code generation
    """
    
    def __init__(self):
        """Initialize Enhanced Utvecklare with cross-repo capabilities."""
        # Get agent configuration
        try:
            self.agent_config = get_agent_config("utvecklare")
        except Exception as e:
            print(f"⚠️  Config issue: {e}")
            # Fallback configuration
            self.agent_config = type('Config', (), {
                'llm_model': 'claude-3-5-sonnet-20241022',
                'temperature': 0.1,
                'max_tokens': 4000,
                'max_iterations': 3
            })()
        
        self.status_handler = StatusHandler()
        
        # Workspace paths for cross-repo operations
        self.product_repo_path = Path("C:/Users/jcols/Documents/diginativa-game")
        self.specs_path = self.product_repo_path / "docs" / "specs"
        self.frontend_path = self.product_repo_path / "frontend" / "src" / "components"
        self.backend_path = self.product_repo_path / "backend" / "app" / "api"
        
        # Verify the real repo exists
        if not self.product_repo_path.exists():
            print(f"❌ Product repo not found at: {self.product_repo_path}")
            print(f"   Expected: C:/Users/jcols/Documents/diginativa-game")
            print(f"   Please clone the diginativa-game repo to this location")
        else:
            print(f"✅ Product repo found at: {self.product_repo_path}")

        # Initialize tools with error handling
        try:
            from tools.dev_tools import EnhancedGitTool
            self.git_tool = EnhancedGitTool()
            self.git_available = True
        except Exception as e:
            print(f"⚠️  Git tool not available: {e}")
            self.git_tool = None
            self.git_available = False
        
        # Claude LLM for code generation
        self.claude_llm = self._create_claude_llm()
        
        # Create the CrewAI agent if available
        if CREWAI_AVAILABLE:
            self.agent = self._create_agent()
        else:
            self.agent = None
            print("⚠️  CrewAI agent not created due to import issues")
        
        print(f"🔨 Enhanced Utvecklare initialized")
        print(f"   Product repo: {GITHUB_CONFIG['project_repo']['name']}")
        print(f"   Frontend: {TECH_STACK['frontend']['framework']}")
        print(f"   Backend: {TECH_STACK['backend']['framework']}")
        print(f"   Model: {self.agent_config.llm_model}")
        print(f"   Git available: {self.git_available}")
        print(f"   CrewAI available: {CREWAI_AVAILABLE}")
    
    def _create_claude_llm(self) -> Optional[ChatAnthropic]:
        """Create Claude LLM optimized for code generation."""
        try:
            anthropic_api_key = SECRETS.get("anthropic_api_key")
            
            if not anthropic_api_key or anthropic_api_key.startswith("[YOUR_"):
                print("⚠️  Anthropic API key not configured")
                return None
            
            claude_llm = ChatAnthropic(
                model=self.agent_config.llm_model,
                api_key=anthropic_api_key,
                temperature=self.agent_config.temperature,
                max_tokens_to_sample=4000
            )
            
            print(f"✅ Claude LLM configured for code generation")
            return claude_llm
            
        except Exception as e:
            print(f"❌ Failed to configure Claude LLM: {e}")
            return None
    
    def _create_agent(self) -> Optional[Agent]:
            """Create the enhanced CrewAI agent with code generation capabilities - FIXED for 0.28.8."""
            if not CREWAI_AVAILABLE or not self.claude_llm:
                return None
                
            try:
                tech_stack_description = (
                    f"{TECH_STACK['frontend']['framework']} + "
                    f"{TECH_STACK['frontend']['language']} + "
                    f"{TECH_STACK['backend']['framework']}"
                )
                
                # FIXED: Create tools WITHOUT importing BaseTool in agent context
                # Use convenience functions instead of tool objects
                agent_tools = []  # Start with empty tools list
                
                return Agent(
                    role=f"Enhanced Full-Stack Developer ({tech_stack_description})",
                    
                    goal=f"""
                    Transform UX specifications into production-ready code for DigiNativa.
                    Generate high-quality {TECH_STACK['frontend']['framework']} components and 
                    {TECH_STACK['backend']['framework']} APIs that exactly match specifications.
                    """,
                    
                    backstory=f"""
                    You are a world-class full-stack developer powered by Claude-3.5-Sonnet, 
                    specializing in the DigiNativa technology stack: {tech_stack_description}.
                    
                    Your development process follows these principles:
                    1. Read and understand UX specifications thoroughly
                    2. Generate backend APIs first, then frontend components
                    3. Ensure all code follows architectural principles
                    4. Create production-ready, testable code
                    5. Validate implementation against specifications
                    
                    You work in the product repository workspace and create:
                    - Frontend: React components with TypeScript
                    - Backend: FastAPI endpoints with proper validation
                    - Clean, maintainable, and well-documented code
                    """,
                    
                    # FIXED: Use empty tools list - we'll use convenience functions instead
                    tools=agent_tools,
                    
                    # FIXED: Explicitly specify Claude LLM instead of default OpenAI
                    llm=self.claude_llm,
                    
                    verbose=True,
                    allow_delegation=False,
                    max_iterations=self.agent_config.max_iterations
                )
                
            except Exception as e:
                print(f"❌ Failed to create CrewAI agent: {e}")
                return None
    
    async def implement_story_from_spec(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Implement a complete story from UX specification.
        
        IMPLEMENTATION WORKFLOW:
        1. Setup workspace and Git branch
        2. Read and parse UX specification
        3. Generate backend API code
        4. Generate frontend component code
        5. Validate implementation
        6. Commit and push changes
        
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
            
            # Step 6: Commit changes to Git
            commit_result = await self._commit_implementation(story_id, story_data, [backend_result, frontend_result])
            
            # Step 7: Create Pull Request
            pr_result = await self._create_pull_request(story_id, story_data, [backend_result, frontend_result])

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
                "git_commit": commit_result,
                "pull_request": pr_result,
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
            
            if not self.git_available:
                return "⚠️  Git tool not available, creating directories only"
            
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
            # Look for specification file in multiple possible locations
            spec_patterns = [
                f"spec-{story_id}.md",
                f"spec_{story_id}.md", 
                f"{story_id}-spec.md",
                f"{story_id}_spec.md"
            ]
            
            spec_content = None
            spec_file_path = None
            
            # First, try in the product repo specs directory
            if self.specs_path.exists():
                for pattern in spec_patterns:
                    potential_path = self.specs_path / pattern
                    if potential_path.exists():
                        spec_file_path = f"workspace/{GITHUB_CONFIG['project_repo']['name']}/docs/specs/{pattern}"
                        spec_content = read_file(spec_file_path, "utvecklare")
                        break
            
            # If not found, try in AI repo docs/specs
            if not spec_content or spec_content.startswith("❌"):
                ai_specs_path = PROJECT_ROOT / "docs" / "specs"
                if ai_specs_path.exists():
                    for pattern in spec_patterns:
                        potential_path = ai_specs_path / pattern
                        if potential_path.exists():
                            spec_file_path = f"docs/specs/{pattern}"
                            spec_content = read_file(spec_file_path, "utvecklare")
                            break
            
            # If still not found, search for any file containing story_id
            if not spec_content or spec_content.startswith("❌"):
                for search_path in [self.specs_path, PROJECT_ROOT / "docs" / "specs"]:
                    if search_path.exists():
                        for spec_file in search_path.glob("*.md"):
                            if story_id in spec_file.name:
                                relative_path = spec_file.relative_to(PROJECT_ROOT)
                                spec_file_path = str(relative_path)
                                spec_content = read_file(spec_file_path, "utvecklare")
                                break
                        if spec_content and not spec_content.startswith("❌"):
                            break
            
            if not spec_content or spec_content.startswith("❌"):
                print(f"❌ No specification found for {story_id}")
                # Create a minimal spec for testing
                return self._create_minimal_spec(story_id)
            
            print(f"📋 Found specification: {spec_file_path}")
            
            # Parse specification content
            parsed_spec = self._parse_specification_content(spec_content)
            parsed_spec["source_file"] = spec_file_path
            
            return parsed_spec
            
        except Exception as e:
            print(f"❌ Failed to read specification for {story_id}: {e}")
            return self._create_minimal_spec(story_id)
    
    def _create_minimal_spec(self, story_id: str) -> Dict[str, Any]:
        """Create a minimal specification for testing when no spec file is found."""
        return {
            "title": f"Feature Implementation for {story_id}",
            "description": "Basic feature implementation with React component and API endpoint",
            "user_value": "Provides functionality to users through clean interface",
            "acceptance_criteria": [
                "Component renders correctly",
                "API endpoint responds with valid data",
                "Error handling works properly",
                "Interface is responsive"
            ],
            "visual_design": "Clean, professional interface following DigiNativa design principles",
            "interaction_flow": "User interacts with component, data fetched from API, results displayed",
            "technical_requirements": "React component with TypeScript, FastAPI endpoint with validation",
            "api_endpoints": ["/api/v1/health"],
            "components": [f"{story_id}Component"]
        }
    
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
                "technical_requirements": {},
                "api_endpoints": [],
                "components": []
            }
            
            # Extract title
            title_match = re.search(r'#\s*(.+)', spec_content)
            if title_match:
                parsed["title"] = title_match.group(1).strip()
            
            # Extract sections using regex
            sections = {
                "description": re.search(r'(?:## .*(?:Description|Beskrivning).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE),
                "user_value": re.search(r'(?:## .*(?:User Value|Användarvärde).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE),
                "visual_design": re.search(r'(?:## .*(?:Visual Design|Visuell Design).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE),
                "technical_requirements": re.search(r'(?:## .*(?:Technical|Teknisk).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE)
            }
            
            for section_name, match in sections.items():
                if match:
                    parsed[section_name] = match.group(1).strip()
            
            # Extract acceptance criteria
            criteria_match = re.search(r'(?:## .*(?:Acceptance Criteria|Acceptanskriterier).*\n)(.*?)(?=\n##|\n#|$)', spec_content, re.DOTALL | re.IGNORECASE)
            if criteria_match:
                criteria_text = criteria_match.group(1)
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
            
            if not self.claude_llm:
                return self._create_fallback_api_design(spec_data)
            
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
            
            if not self.claude_llm:
                # Fallback: Create basic backend code
                backend_code = self._create_fallback_backend_code(story_id, spec_data)
            else:
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
            
            # FIXED: Write to real diginativa-game repo, not workspace
            backend_file_path = self.backend_path / f"{story_id}.py"
            backend_file_relative = f"backend/app/api/{story_id}.py"
            
            # Use absolute path for writing, relative path for Git operations
            write_result = write_file(str(backend_file_path), backend_code, "utvecklare")
            
            if "successfully" not in write_result.lower():
                raise Exception(f"Failed to write backend file: {write_result}")
            
            print(f"✅ Backend code generated: {backend_file_relative}")
            
            return {
                "status": "success",
                "files_created": [backend_file_relative],  # Relative path for Git
                "absolute_path": str(backend_file_path),    # Absolute path for reference
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
    
    def _create_fallback_backend_code(self, story_id: str, spec_data: Dict[str, Any]) -> str:
        """Create basic FastAPI code when Claude is not available."""
        return f'''"""
{spec_data.get('title', 'Generated Feature')} - FastAPI Backend
Generated by DigiNativa AI Utvecklare

Story ID: {story_id}
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    story_id: str

class {story_id.replace('-', '_')}_Response(BaseModel):
    message: str
    data: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(title="{spec_data.get('title', 'Generated Feature')}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        story_id="{story_id}"
    )

@app.get("/{story_id.lower()}", response_model={story_id.replace('-', '_')}_Response)
async def get_{story_id.replace('-', '_').lower()}():
    """Main endpoint for {spec_data.get('title', 'feature')}"""
    return {story_id.replace('-', '_')}_Response(
        message="Feature implemented successfully",
        data={{
            "story_id": "{story_id}",
            "title": "{spec_data.get('title', 'Generated Feature')}",
            "status": "active"
        }}
    )
'''
    
    async def _generate_frontend_code(self, story_id: str, spec_data: Dict[str, Any], api_design: Dict[str, Any]) -> Dict[str, Any]:
        """Generate React frontend component based on specification and API design."""
        try:
            print(f"🎨 Generating frontend code for {story_id}")
            
            if not self.claude_llm:
                # Fallback: Create basic React component
                frontend_code = self._create_fallback_frontend_code(story_id, spec_data)
            else:
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
            
            # FIXED: Write to real diginativa-game repo, not workspace
            frontend_file_path = self.frontend_path / f"{story_id}.tsx"
            frontend_file_relative = f"frontend/src/components/{story_id}.tsx"
            
            # Use absolute path for writing, relative path for Git operations
            write_result = write_file(str(frontend_file_path), frontend_code, "utvecklare")
            
            if "successfully" not in write_result.lower():
                raise Exception(f"Failed to write frontend file: {write_result}")
            
            print(f"✅ Frontend code generated: {frontend_file_relative}")
            
            return {
                "status": "success",
                "files_created": [frontend_file_relative],  # Relative path for Git
                "absolute_path": str(frontend_file_path),    # Absolute path for reference
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
    
    def _create_fallback_frontend_code(self, story_id: str, spec_data: Dict[str, Any]) -> str:
        """Create basic React component when Claude is not available."""
        component_name = story_id.replace('-', '_').replace('_', '')
        
        return f'''/**
 * {spec_data.get('title', 'Generated Feature')} - React Component
 * Generated by DigiNativa AI Utvecklare
 * 
 * Story ID: {story_id}
 */

import React, {{ useState, useEffect }} from 'react';

interface {component_name}Props {{
  className?: string;
}}

interface {component_name}Data {{
  message: string;
  data: {{
    story_id: string;
    title: string;
    status: string;
  }};
}}

const {component_name}: React.FC<{component_name}Props> = ({{ className = '' }}) => {{
  const [data, setData] = useState<{component_name}Data | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {{
    const fetchData = async () => {{
      try {{
        setLoading(true);
        const response = await fetch('/api/v1/{story_id.lower()}');
        
        if (!response.ok) {{
          throw new Error(`HTTP error! status: ${{response.status}}`);
        }}
        
        const result = await response.json();
        setData(result);
        setError(null);
      }} catch (err) {{
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        setData(null);
      }} finally {{
        setLoading(false);
      }}
    }};

    fetchData();
  }}, []);

  if (loading) {{
    return (
      <div className={{`flex items-center justify-center p-8 ${{className}}`}}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading...</span>
      </div>
    );
  }}

  if (error) {{
    return (
      <div className={{`bg-red-50 border border-red-200 rounded-lg p-4 ${{className}}`}}>
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error Loading Data</h3>
            <p className="mt-1 text-sm text-red-700">{{error}}</p>
          </div>
        </div>
      </div>
    );
  }}

  return (
    <div className={{`bg-white shadow rounded-lg p-6 ${{className}}`}}>
      <div className="border-b border-gray-200 pb-4 mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          {spec_data.get('title', 'Generated Feature')}
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Story ID: {story_id}
        </p>
      </div>
      
      {{data && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium text-gray-700">Status</h3>
            <p className="mt-1 text-sm text-gray-900">{{data.data.status}}</p>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-gray-700">Message</h3>
            <p className="mt-1 text-sm text-gray-900">{{data.message}}</p>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-blue-800">Feature Information</h4>
            <dl className="mt-2 text-sm text-blue-700">
              <div className="flex justify-between">
                <dt>Title:</dt>
                <dd>{{data.data.title}}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Story ID:</dt>
                <dd>{{data.data.story_id}}</dd>
              </div>
            </dl>
          </div>
        </div>
      )}}
    </div>
  );
}};

export default {component_name};
'''
    
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
    
    async def _create_pull_request(self, story_id: str, story_data: Dict[str, Any], 
                                implementation_results: List[Dict[str, Any]]) -> str:
        """Create pull request for the implemented feature."""
        try:
            print(f"🔄 Creating pull request for {story_id}")
            
            if not self.git_available:
                return "⚠️  Git not available, PR creation skipped"
            
            # Create PR title and description
            story_title = story_data.get("title", "Unknown feature")
            pr_title = f"feat({story_id}): {story_title}"
            
            # Count files from implementation results
            backend_files = []
            frontend_files = []
            
            for result in implementation_results:
                if "backend" in str(result.get("files_created", [])):
                    backend_files.extend(result.get("files_created", []))
                else:
                    frontend_files.extend(result.get("files_created", []))
            
            # If we can't categorize, use the results directly
            if not backend_files and not frontend_files:
                if len(implementation_results) >= 2:
                    backend_files = implementation_results[0].get("files_created", [])
                    frontend_files = implementation_results[1].get("files_created", [])
            
            pr_body = f"""## 🤖 AI-Generated Feature Implementation

    **Story ID**: {story_id}
    **Feature**: {story_title}
    **Generated by**: DigiNativa AI Utvecklare (Claude-3.5-Sonnet)

    ### 📁 Files Created
    - **Backend**: {len(backend_files)} files
    - **Frontend**: {len(frontend_files)} files

    ### 🔧 Implementation Details
    """
            
            for file_path in backend_files:
                file_name = Path(file_path).name if file_path else "unknown"
                pr_body += f"- 🔌 Backend API: `{file_name}`\n"
            for file_path in frontend_files:
                file_name = Path(file_path).name if file_path else "unknown"
                pr_body += f"- ⚛️ React Component: `{file_name}`\n"
            
            pr_body += f"""
    ### ✅ Ready for Review
    - [ ] Code follows DigiNativa architecture principles
    - [ ] Responsive design implemented
    - [ ] API endpoints functional
    - [ ] Error handling included

    ### 🧪 Testing
    1. Check out this branch: `git checkout feature/{story_id}-*`
    2. Start backend: `cd backend && uvicorn app.main:app --reload`
    3. Start frontend: `cd frontend && npm start`
    4. Test the feature functionality

    **Estimated review time**: 15-30 minutes

    ---
    *This PR was automatically created by the DigiNativa AI development team*
    """
            
            # Create PR through Git tool
            pr_result = self.git_tool._run('create_pull_request',
                                        pr_title=pr_title,
                                        pr_body=pr_body,
                                        story_id=story_id,
                                        target_repo='product_repo')
            
            if "✅" in pr_result:
                print(f"✅ Pull request created successfully")
            else:
                print(f"⚠️  PR creation result: {pr_result}")
            
            return pr_result
            
        except Exception as e:
            return f"❌ PR creation failed: {str(e)}"


    async def _commit_implementation(self, story_id: str, story_data: Dict[str, Any], implementation_results: List[Dict[str, Any]]) -> str:
        """Commit implementation to Git with proper commit message."""
        try:
            print(f"📝 Committing implementation for {story_id}")
            
            if not self.git_available:
                return "⚠️  Git not available, files created but not committed"
            
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

    async def _create_pull_request(self, story_id: str, story_data: Dict[str, Any], 
                                implementation_results: List[Dict[str, Any]]) -> str:
        """Create pull request for the implemented feature."""
        try:
            print(f"🔄 Creating pull request for {story_id}")
            
            if not self.git_available:
                return "⚠️  Git not available, PR creation skipped"
            
            # Create PR title and description
            story_title = story_data.get("title", "Unknown feature")
            pr_title = f"feat({story_id}): {story_title}"
            
            # Count files
            backend_files = implementation_results[0].get("files_created", [])
            frontend_files = implementation_results[1].get("files_created", [])
            
            pr_body = f"""## 🤖 AI-Generated Feature Implementation

    **Story ID**: {story_id}
    **Feature**: {story_title}
    **Generated by**: DigiNativa AI Utvecklare (Claude-3.5-Sonnet)

    ### 📁 Files Created
    - **Backend**: {len(backend_files)} files
    - **Frontend**: {len(frontend_files)} files

    ### 🔧 Implementation Details
    """
            
            for file_path in backend_files:
                pr_body += f"- 🔌 Backend API: `{Path(file_path).name}`\n"
            for file_path in frontend_files:
                pr_body += f"- ⚛️ React Component: `{Path(file_path).name}`\n"
            
            pr_body += f"""
    ### ✅ Ready for Review
    - [ ] Code follows DigiNativa architecture principles
    - [ ] Responsive design implemented
    - [ ] API endpoints functional
    - [ ] Error handling included

    ### 🧪 Testing
    1. Check out this branch: `git checkout feature/{story_id}-*`
    2. Start backend: `cd backend && uvicorn app.main:app --reload`
    3. Start frontend: `cd frontend && npm start`
    4. Test the feature functionality

    **Estimated review time**: 15-30 minutes

    ---
    *This PR was automatically created by the DigiNativa AI development team*
    """
            
            # Create PR through Git tool
            pr_result = self.git_tool._run('create_pull_request',
                                        pr_title=pr_title,
                                        pr_body=pr_body,
                                        story_id=story_id,
                                        target_repo='product_repo')
            
            if "✅" in pr_result:
                print(f"✅ Pull request created successfully")
            else:
                print(f"⚠️  PR creation result: {pr_result}")
            
            return pr_result
            
        except Exception as e:
            return f"❌ PR creation failed: {str(e)}"

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

# Convenience function for simple code generation test
def test_code_generation_simple() -> bool:
    """Test basic code generation without full workflow."""
    try:
        print("🧪 Testing simple code generation...")
        
        # Create agent
        utvecklare = create_enhanced_utvecklare_agent()
        
        # Test that basic components are working
        assert utvecklare is not None
        assert hasattr(utvecklare, 'claude_llm')
        assert hasattr(utvecklare, 'git_tool') or not utvecklare.git_available
        
        print("✅ Basic agent creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        return False

if __name__ == "__main__":
    # Test script for debugging and development
    import asyncio
    
    async def test_enhanced_utvecklare():
        """Test script for Enhanced Utvecklare functionality."""
        print("🧪 Testing Enhanced Utvecklare agent...")
        
        try:
            # Test 1: Simple creation test
            if not test_code_generation_simple():
                print("❌ Basic test failed, skipping advanced tests")
                return
            
            # Test 2: Demo implementation
            print("\n🔨 Testing demo implementation...")
            result = await implement_demo_story("TEST-DEV-001")
            
            if result.get("implementation_status") == "completed":
                print("✅ Enhanced Utvecklare test completed successfully!")
                print(f"   Backend files: {len(result.get('backend_files', []))}")
                print(f"   Frontend files: {len(result.get('frontend_files', []))}")
                print(f"   Git commit: {result.get('git_commit', 'N/A')}")
            else:
                print(f"⚠️  Demo implementation completed with issues:")
                print(f"   Status: {result.get('implementation_status', 'unknown')}")
                if result.get('error'):
                    print(f"   Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    # Run test if script is executed directly
    asyncio.run(test_enhanced_utvecklare())