"""
DigiNativa AI-Agent: Utvecklare (Simplified)
==========================================

PURPOSE:
Simplified Utvecklare that generates React + FastAPI code from UX specifications
without complex tool inheritance or cross-repo complications.

RESPONSIBILITIES:
1. Read UX specifications
2. Generate React components
3. Generate FastAPI endpoints
4. Create simple, production-ready code

SIMPLIFIED ARCHITECTURE:
- Direct Claude LLM interaction
- Simple file operations to local directories
- Focus on core code generation
- Clear error handling
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("⚠️  langchain_anthropic not available")
    ANTHROPIC_AVAILABLE = False
    ChatAnthropic = None

from config.settings import SECRETS, TECH_STACK
from tools.file_utils import read_file, write_file, read_spec_file
from workflows.status_handler import StatusHandler


class UtvecklareAgent:
    """
    Simplified Utvecklare agent for DigiNativa AI team.
    
    Generates production-ready React + FastAPI code from specifications.
    """
    
    def __init__(self):
        """Initialize Utvecklare with Claude LLM."""
        print("🔨 Initializing Utvecklare (Simplified)...")
        
        # Initialize Claude LLM
        self.claude_llm = self._create_claude_llm()
        
        # Set up output directories
        self.frontend_dir = Path("frontend/src/components")
        self.backend_dir = Path("backend/app/api")
        
        # Ensure directories exist
        self.frontend_dir.mkdir(parents=True, exist_ok=True)
        self.backend_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Utvecklare ready")
        print(f"   Claude available: {self.claude_llm is not None}")
        print(f"   Frontend: {TECH_STACK['frontend']['framework']}")
        print(f"   Backend: {TECH_STACK['backend']['framework']}")
    
    def _create_claude_llm(self) -> Optional[ChatAnthropic]:
        """Create Claude LLM for code generation."""
        if not ANTHROPIC_AVAILABLE:
            print("⚠️  Claude not available")
            return None
        
        try:
            api_key = SECRETS.get("anthropic_api_key")
            if not api_key or api_key.startswith("[YOUR_"):
                print("⚠️  Anthropic API key not configured")
                return None
            
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=api_key,
                temperature=0.1,  # Low temperature for consistent code
                max_tokens_to_sample=4000
            )
            
        except Exception as e:
            print(f"⚠️  Claude initialization failed: {e}")
            return None
    
    async def implement_from_specification(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code from UX specification.
        
        Args:
            story_data: Story information with story_id, title, etc.
            
        Returns:
            Implementation results with file paths and status
        """
        start_time = datetime.now()
        story_id = story_data.get("story_id", "UNKNOWN")
        
        try:
            print(f"🔨 Implementing {story_id}...")
            
            # Read specification
            spec_content = read_spec_file(story_id)
            if spec_content.startswith("❌"):
                # Try alternative specification sources
                spec_content = self._get_specification_from_story_data(story_data)
            
            print(f"   Specification loaded: {len(spec_content)} characters")
            
            # Generate API design
            api_design = await self._design_api_from_spec(spec_content, story_data)
            
            # Generate backend code
            backend_result = await self._generate_backend_code(story_id, spec_content, api_design)
            
            # Generate frontend code  
            frontend_result = await self._generate_frontend_code(story_id, spec_content, api_design)
            
            # Compile results
            results = {
                "story_id": story_id,
                "status": "completed",
                "backend_files": backend_result.get("files_created", []),
                "frontend_files": frontend_result.get("files_created", []),
                "api_endpoints": api_design.get("endpoints", []),
                "implementation_time_seconds": (datetime.now() - start_time).total_seconds(),
                "created_at": datetime.now().isoformat()
            }
            
            print(f"✅ Implementation completed")
            print(f"   Backend files: {len(results['backend_files'])}")
            print(f"   Frontend files: {len(results['frontend_files'])}")
            print(f"   API endpoints: {len(results['api_endpoints'])}")
            
            return results
            
        except Exception as e:
            error_msg = f"Implementation failed for {story_id}: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                "story_id": story_id,
                "status": "failed",
                "error": error_msg,
                "created_at": datetime.now().isoformat()
            }
    
    def _get_specification_from_story_data(self, story_data: Dict[str, Any]) -> str:
        """Create basic specification from story data when no spec file exists."""
        title = story_data.get("title", "Unknown Feature")
        description = story_data.get("description", "")
        
        return f"""# UX Specification: {title}

## Description
{description}

## Basic Requirements
- Create React component for {title}
- Implement FastAPI endpoint for data
- Ensure responsive design
- Follow DigiNativa design principles

## Acceptance Criteria
- Component renders correctly
- API returns valid data
- Interface is responsive
- Error handling works
"""
    
    async def _design_api_from_spec(self, spec_content: str, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design API endpoints based on specification."""
        try:
            if not self.claude_llm:
                return self._create_fallback_api_design(story_data)
            
            story_id = story_data.get("story_id", "unknown")
            
            prompt = f"""
            Design a simple FastAPI endpoint for this feature.

            SPECIFICATION:
            {spec_content[:1500]}  # Limit to avoid token limits

            REQUIREMENTS:
            - Single GET endpoint that returns data
            - Pydantic response model
            - Simple, stateless design
            - Response time <200ms

            Return ONLY valid JSON in this format:
            {{
                "endpoints": [
                    {{
                        "method": "GET",
                        "path": "/api/v1/{story_id.lower().replace('-', '_')}",
                        "description": "Brief description",
                        "response_model": {{"field": "type"}}
                    }}
                ],
                "models": [
                    {{
                        "name": "ResponseModel",
                        "fields": {{"field": "type"}}
                    }}
                ]
            }}
            """
            
            response = self.claude_llm.invoke(prompt)
            
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                print("⚠️  Failed to parse API design, using fallback")
                return self._create_fallback_api_design(story_data)
            
        except Exception as e:
            print(f"⚠️  API design error: {e}")
            return self._create_fallback_api_design(story_data)
    
    def _create_fallback_api_design(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic API design when Claude fails."""
        story_id = story_data.get("story_id", "unknown")
        endpoint_name = story_id.lower().replace('-', '_')
        
        return {
            "endpoints": [
                {
                    "method": "GET",
                    "path": f"/api/v1/{endpoint_name}",
                    "description": f"Get data for {story_data.get('title', 'feature')}",
                    "response_model": {"message": "str", "data": "dict"}
                }
            ],
            "models": [
                {
                    "name": f"{endpoint_name.title()}Response",
                    "fields": {"message": "str", "data": "Dict[str, Any]"}
                }
            ]
        }
    
    async def _generate_backend_code(self, story_id: str, spec_content: str, 
                                   api_design: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FastAPI backend code."""
        try:
            print(f"⚙️  Generating backend code...")
            
            if self.claude_llm:
                backend_code = await self._generate_backend_with_claude(story_id, spec_content, api_design)
            else:
                backend_code = self._create_fallback_backend_code(story_id, api_design)
            
            # Clean code
            backend_code = self._clean_generated_code(backend_code)
            
            # Save file
            filename = f"{story_id.lower().replace('-', '_')}.py"
            file_path = f"backend/app/api/{filename}"
            
            result = write_file(file_path, backend_code)
            
            if result.startswith("✅"):
                return {
                    "status": "success",
                    "files_created": [file_path],
                    "code_length": len(backend_code)
                }
            else:
                return {
                    "status": "failed",
                    "error": result,
                    "files_created": []
                }
                
        except Exception as e:
            print(f"❌ Backend generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "files_created": []
            }
    
    async def _generate_backend_with_claude(self, story_id: str, spec_content: str, 
                                          api_design: Dict[str, Any]) -> str:
        """Generate backend code using Claude."""
        prompt = f"""
        Generate production-ready FastAPI code for this feature.

        STORY ID: {story_id}
        API DESIGN: {json.dumps(api_design, indent=2)}

        Create a complete Python file with:
        - FastAPI router
        - Pydantic models  
        - Proper error handling
        - Type hints
        - Docstrings

        Focus on clean, simple, production-ready code.
        """
        
        response = self.claude_llm.invoke(prompt)
        return response.content
    
    def _create_fallback_backend_code(self, story_id: str, api_design: Dict[str, Any]) -> str:
        """Create basic backend code when Claude fails."""
        endpoint_name = story_id.lower().replace('-', '_')
        class_name = endpoint_name.replace('_', '').title()
        
        return f'''"""
FastAPI Backend for {story_id}
Generated by DigiNativa Utvecklare
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

# Router for this feature
router = APIRouter(prefix="/api/v1", tags=["{story_id}"])

# Response model
class {class_name}Response(BaseModel):
    message: str
    data: Dict[str, Any]
    timestamp: str

@router.get("/{endpoint_name}", response_model={class_name}Response)
async def get_{endpoint_name}():
    """
    Get data for {story_id} feature.
    
    Returns:
        Response with feature data
    """
    try:
        # Generate sample data
        feature_data = {{
            "story_id": "{story_id}",
            "status": "active",
            "title": "Generated Feature"
        }}
        
        return {class_name}Response(
            message="Feature data retrieved successfully",
            data=feature_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    async def _generate_frontend_code(self, story_id: str, spec_content: str, 
                                    api_design: Dict[str, Any]) -> Dict[str, Any]:
        """Generate React frontend component."""
        try:
            print(f"🎨 Generating frontend code...")
            
            if self.claude_llm:
                frontend_code = await self._generate_frontend_with_claude(story_id, spec_content, api_design)
            else:
                frontend_code = self._create_fallback_frontend_code(story_id, api_design)
            
            # Clean code
            frontend_code = self._clean_generated_code(frontend_code)
            
            # Save file
            component_name = story_id.replace('-', '')
            filename = f"{component_name}.tsx"
            file_path = f"frontend/src/components/{filename}"
            
            result = write_file(file_path, frontend_code)
            
            if result.startswith("✅"):
                return {
                    "status": "success", 
                    "files_created": [file_path],
                    "component_name": component_name,
                    "code_length": len(frontend_code)
                }
            else:
                return {
                    "status": "failed",
                    "error": result,
                    "files_created": []
                }
                
        except Exception as e:
            print(f"❌ Frontend generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "files_created": []
            }
    
    async def _generate_frontend_with_claude(self, story_id: str, spec_content: str, 
                                           api_design: Dict[str, Any]) -> str:
        """Generate frontend code using Claude."""
        component_name = story_id.replace('-', '')
        
        prompt = f"""
        Generate a production-ready React TypeScript component.

        COMPONENT NAME: {component_name}
        STORY ID: {story_id}
        API ENDPOINTS: {json.dumps(api_design.get('endpoints', []), indent=2)}

        Create a complete TSX file with:
        - React functional component with hooks
        - TypeScript interfaces
        - Tailwind CSS styling
        - Error handling and loading states
        - Responsive design
        - Professional appearance for Swedish public sector

        Focus on clean, accessible, production-ready code.
        """
        
        response = self.claude_llm.invoke(prompt)
        return response.content
    
    def _create_fallback_frontend_code(self, story_id: str, api_design: Dict[str, Any]) -> str:
        """Create basic frontend code when Claude fails."""
        component_name = story_id.replace('-', '')
        endpoint_path = api_design.get('endpoints', [{}])[0].get('path', '/api/v1/data')
        
        return f'''/**
 * {component_name} Component
 * Generated by DigiNativa Utvecklare
 * Story ID: {story_id}
 */

import React, {{ useState, useEffect }} from 'react';

interface {component_name}Data {{
  message: string;
  data: {{
    story_id: string;
    status: string;
    title: string;
  }};
  timestamp: string;
}}

interface {component_name}Props {{
  className?: string;
}}

const {component_name}: React.FC<{component_name}Props> = ({{ className = '' }}) => {{
  const [data, setData] = useState<{component_name}Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {{
    const fetchData = async () => {{
      try {{
        setLoading(true);
        const response = await fetch('{endpoint_path}');
        
        if (!response.ok) {{
          throw new Error(`HTTP error! status: ${{response.status}}`);
        }}
        
        const result = await response.json();
        setData(result);
        setError(null);
      }} catch (err) {{
        setError(err instanceof Error ? err.message : 'Unknown error');
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
            <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
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
          {story_id} Feature
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Generated component for DigiNativa
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
            <h4 className="text-sm font-medium text-blue-800">Feature Details</h4>
            <dl className="mt-2 text-sm text-blue-700">
              <div className="flex justify-between">
                <dt>Story ID:</dt>
                <dd>{{data.data.story_id}}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Title:</dt>
                <dd>{{data.data.title}}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Updated:</dt>
                <dd>{{new Date(data.timestamp).toLocaleString()}}</dd>
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
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean and format generated code."""
        # Remove markdown code blocks if present
        if "```" in code:
            code_blocks = re.findall(r'```(?:python|typescript|tsx|javascript)?\n(.*?)```', code, re.DOTALL)
            if code_blocks:
                code = code_blocks[0]
        
        # Clean up excessive whitespace
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_lines.append(line.rstrip())
        
        # Remove excessive blank lines
        final_lines = []
        blank_count = 0
        
        for line in cleaned_lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 2:
                    final_lines.append(line)
            else:
                blank_count = 0
                final_lines.append(line)
        
        return '\n'.join(final_lines)

# Factory function for easy usage
def create_utvecklare_agent() -> UtvecklareAgent:
    """Create simplified Utvecklare agent."""
    return UtvecklareAgent()

# Test function
async def test_utvecklare():
    """Test Utvecklare functionality."""
    print("🧪 Testing Simplified Utvecklare...")
    
    try:
        # Create agent
        utvecklare = create_utvecklare_agent()
        
        # Test implementation
        test_story = {
            "story_id": "TEST-DEV-001",
            "title": "User Dashboard Component",
            "description": "Create dashboard for Anna to view her progress"
        }
        
        result = await utvecklare.implement_from_specification(test_story)
        
        if result.get("status") == "completed":
            print("✅ Implementation completed successfully")
            print(f"   Backend files: {len(result.get('backend_files', []))}")
            print(f"   Frontend files: {len(result.get('frontend_files', []))}")
        else:
            print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_utvecklare())
