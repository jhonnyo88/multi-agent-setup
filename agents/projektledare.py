"""
DigiNativa Projektledare Agent (Minimal Version)
===============================================

PURPOSE:
Simplified Projektledare without agent coordinator complexity.
Focuses on GitHub integration and basic workflow management.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("⚠️  langchain_anthropic not available")
    ANTHROPIC_AVAILABLE = False
    ChatAnthropic = None

from config.settings import SECRETS, PROJECT_NAME, TECH_STACK
from workflows.status_handler import StatusHandler

# Try to import GitHub integration with error handling
try:
    from workflows.github_integration.project_owner_communication import ProjectOwnerCommunication
    GITHUB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  GitHub integration not available: {e}")
    GITHUB_AVAILABLE = False
    ProjectOwnerCommunication = None

class ProjektledareAgent:
    """
    Simplified Projektledare agent for DigiNativa AI team.
    
    Handles GitHub integration and basic project management without
    complex coordination or exception handling systems.
    """
    
    def __init__(self):
        """Initialize Projektledare with essential components."""
        print("🎯 Initializing Projektledare (Simplified)...")
        
        self.status_handler = StatusHandler()
        self.claude_llm = self._create_claude_llm()
        
        # Initialize GitHub communication if available
        if GITHUB_AVAILABLE:
            try:
                self.github_comm = ProjectOwnerCommunication()
                print("✅ GitHub integration ready")
            except Exception as e:
                print(f"⚠️  GitHub integration failed: {e}")
                self.github_comm = None
        else:
            self.github_comm = None
        
        print(f"✅ Projektledare initialized")
        print(f"   Project: {PROJECT_NAME}")
        print(f"   Claude available: {self.claude_llm is not None}")
        print(f"   GitHub available: {self.github_comm is not None}")
    
    def _create_claude_llm(self) -> Optional[ChatAnthropic]:
        """Create Claude LLM for analysis and planning."""
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
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens_to_sample=4000
            )
            
        except Exception as e:
            print(f"⚠️  Claude initialization failed: {e}")
            return None
    
    async def analyze_feature_request(self, github_issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a GitHub Issue containing a feature request.
        
        Args:
            github_issue: GitHub Issue data
            
        Returns:
            Analysis results with recommendation
        """
        try:
            print(f"🔍 Analyzing feature request...")
            
            issue_title = github_issue.get("title", "Unknown Feature")
            issue_body = github_issue.get("body", "")
            
            print(f"   Feature: {issue_title}")
            
            if self.claude_llm:
                analysis = await self._analyze_with_claude(issue_title, issue_body)
            else:
                analysis = self._create_fallback_analysis(issue_title, issue_body)
            
            # Log analysis
            self.status_handler.report_status(
                agent_name="projektledare",
                status_code="FEATURE_ANALYZED",
                payload={
                    "issue_title": issue_title,
                    "recommendation": analysis.get("recommendation", {}).get("action"),
                    "ai_model": "claude-3-5-sonnet" if self.claude_llm else "fallback"
                }
            )
            
            print(f"✅ Analysis completed: {analysis.get('recommendation', {}).get('action', 'unknown')}")
            return analysis
            
        except Exception as e:
            error_msg = f"Feature analysis failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                "error": error_msg,
                "recommendation": {"action": "error", "reasoning": error_msg}
            }
    
    async def _analyze_with_claude(self, title: str, description: str) -> Dict[str, Any]:
        """Analyze feature using Claude."""
        prompt = f"""
        Analyze this feature request for DigiNativa (Swedish public sector digitalization game).

        TITLE: {title}
        DESCRIPTION: {description}

        Consider:
        - Educational value for public sector professionals
        - Time constraints (<10 minute sessions)
        - Technical feasibility with React + FastAPI
        - Alignment with professional learning goals

        Return ONLY valid JSON:
        {{
            "recommendation": {{
                "action": "approve|reject|clarify",
                "reasoning": "Brief explanation",
                "priority": "high|medium|low"
            }},
            "complexity": {{
                "estimated_days": 3-7,
                "estimated_stories": 2-5
            }},
            "technical_notes": ["React component needed", "API endpoint required"]
        }}
        """
        
        try:
            response = self.claude_llm.invoke(prompt)
            return json.loads(response.content)
        except Exception as e:
            print(f"⚠️  Claude analysis failed: {e}")
            return self._create_fallback_analysis(title, description)
    
    def _create_fallback_analysis(self, title: str, description: str) -> Dict[str, Any]:
        """Create basic analysis when Claude is not available."""
        return {
            "recommendation": {
                "action": "approve",
                "reasoning": "Basic approval - manual review recommended",
                "priority": "medium"
            },
            "complexity": {
                "estimated_days": 5,
                "estimated_stories": 3
            },
            "technical_notes": [
                "React component implementation needed",
                "FastAPI endpoint required",
                "Manual analysis - review recommended"
            ]
        }
    
    async def create_story_breakdown(self, feature_analysis: Dict[str, Any], 
                                   github_issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create story breakdown from analyzed feature.
        
        Args:
            feature_analysis: Results from analyze_feature_request
            github_issue: Original GitHub issue
            
        Returns:
            List of story definitions
        """
        try:
            print(f"📋 Creating story breakdown...")
            
            issue_title = github_issue.get("title", "Unknown Feature")
            issue_number = github_issue.get("number", 999)
            story_base_id = f"STORY-{issue_number:03d}"
            
            stories = []
            
            # Story 1: UX Specification
            stories.append({
                "story_id": f"{story_base_id}-001",
                "title": f"UX Specification: {issue_title}",
                "description": f"Create detailed UX specification for {issue_title}",
                "assigned_agent": "speldesigner",
                "story_type": "specification",
                "acceptance_criteria": [
                    "UX specification document created",
                    "Design principles validated",
                    "Acceptance criteria defined",
                    "Visual design guidelines provided"
                ],
                "estimated_effort": "Medium"
            })
            
            # Story 2: Implementation
            stories.append({
                "story_id": f"{story_base_id}-002",
                "title": f"Implementation: {issue_title}",
                "description": f"Implement React component and FastAPI endpoint for {issue_title}",
                "assigned_agent": "utvecklare",
                "story_type": "implementation",
                "acceptance_criteria": [
                    "React component implemented",
                    "FastAPI endpoint created",
                    "Responsive design implemented",
                    "Error handling included"
                ],
                "estimated_effort": "Large"
            })
            
            print(f"✅ Created {len(stories)} stories")
            return stories
            
        except Exception as e:
            print(f"❌ Story breakdown failed: {e}")
            return []
    
    async def monitor_github_features(self) -> List[Dict[str, Any]]:
        """Monitor GitHub for new feature requests."""
        if not self.github_comm:
            print("⚠️  GitHub integration not available")
            return []
        
        try:
            print("🔍 Monitoring GitHub for new features...")
            return await self.github_comm.process_new_features()
        except Exception as e:
            print(f"❌ GitHub monitoring failed: {e}")
            return []

# Factory function
def create_projektledare() -> ProjektledareAgent:
    """Create simplified Projektledare agent."""
    return ProjektledareAgent()

# Test function
async def test_projektledare():
    """Test Projektledare functionality."""
    print("🧪 Testing Simplified Projektledare...")
    
    try:
        # Create agent
        projektledare = create_projektledare()
        
        # Test analysis
        test_issue = {
            "title": "User Progress Dashboard",
            "body": "Create dashboard for Anna to track her learning progress",
            "number": 123
        }
        
        analysis = await projektledare.analyze_feature_request(test_issue)
        
        if "error" not in analysis:
            print("✅ Feature analysis works")
            print(f"   Recommendation: {analysis.get('recommendation', {}).get('action')}")
            
            # Test story breakdown
            stories = await projektledare.create_story_breakdown(analysis, test_issue)
            print(f"✅ Story breakdown created: {len(stories)} stories")
        else:
            print(f"❌ Analysis failed: {analysis['error']}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_projektledare())