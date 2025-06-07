"""
Enhanced Design Tools for DigiNativa Speldesigner Agent
======================================================

PURPOSE:
Specialized tools that give the Speldesigner agent cognitive abilities to validate
their own specifications against the project's core principles (DNA) and ensure
all designs meet quality standards before being handed over to development.

CREWAI COMPATIBILITY:
Updated to work with CrewAI's current tool system and Claude integration.
Uses proper CrewAI BaseTool imports and error handling.

ADAPTATION GUIDE:
🔧 To adapt these tools:
1. Update the design principles validation logic for your domain
2. Modify the acceptance criteria patterns for your quality requirements
3. Adjust the scoring system for your project standards
4. Customize the prompt templates for your specific context
"""

import os
import json
import re
from typing import List, Type, Optional, Dict, Any
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic

# Import configuration and dependencies
from config.settings import AGENT_CONFIG, SECRETS, DNA_DIR, PROJECT_ROOT
from tools.file_tools import read_file

# --- Input Models for Tools ---

class DesignValidationInput(BaseModel):
    """Input schema for design validation tools."""
    specification_text: str = Field(
        ..., 
        description="The complete text of the design specification to be reviewed against design principles."
    )

class AcceptanceCriteriaInput(BaseModel):
    """Input schema for acceptance criteria validation."""
    criteria_list: List[str] = Field(
        ..., 
        description="A list of acceptance criteria to be validated for testability and clarity."
    )

class UserStoryInput(BaseModel):
    """Input schema for user story validation."""
    user_story: str = Field(
        ...,
        description="A user story to validate against Anna persona and project goals."
    )

# --- Specialized Design Tools ---

class DesignPrinciplesValidatorTool(BaseTool):
    """
    Tool for validating design specifications against DigiNativa's 5 core design principles.
    
    This tool ensures that every design decision serves the project's educational mission
    and meets the specific needs of Swedish public sector employees like "Anna".
    """
    name: str = "Design Principles Validator"
    description: str = (
        "Validate a design specification against DigiNativa's 5 core design principles: "
        "1) Pedagogik Framför Allt, 2) Policy till Praktik, 3) Respekt för Tid, "
        "4) Helhetssyn Genom Handling, 5) Intelligens Inte Infantilisering. "
        "Returns scored validation with reasoning for each principle."
    )
    args_schema: Type[BaseModel] = DesignValidationInput
    claude_llm: Optional[ChatAnthropic] = None
    principles_cache: Optional[str] = None
    
    def __init__(self):
        super().__init__()
        self.claude_llm = self._create_claude_llm()
        self.principles_cache = None

    def _create_claude_llm(self) -> Optional[ChatAnthropic]:
        """Create Claude LLM instance with error handling."""
        try:
            api_key = SECRETS.get("anthropic_api_key")
            if not api_key or api_key.startswith("[YOUR_"):
                print("⚠️  Warning: Anthropic API key not configured for design tools")
                return None
                
            return ChatAnthropic(
                model=AGENT_CONFIG["llm_model"],
                api_key=api_key,
                temperature=0.1,  # Low temperature for consistent validation
                max_tokens_to_sample=2000
            )
        except Exception as e:
            print(f"⚠️  Could not initialize Claude LLM for design tools: {e}")
            return None

    def _load_design_principles(self) -> str:
        """Load design principles from DNA documents."""
        if self.principles_cache is None:
            try:
                principles_path = DNA_DIR / "design_principles.md"
                if principles_path.exists():
                    self.principles_cache = read_file(str(principles_path), agent_name="design_validator")
                else:
                    # Fallback to default principles if file not found
                    self.principles_cache = self._get_default_principles()
            except Exception as e:
                print(f"⚠️  Could not load design principles: {e}")
                self.principles_cache = self._get_default_principles()
        
        return self.principles_cache

    def _get_default_principles(self) -> str:
        """Default design principles if DNA document is not available."""
        return """
        # DigiNativa Design Principles
        
        1. **Pedagogik Framför Allt**: Every element must serve an educational purpose
        2. **Policy till Praktik**: Bridge abstract strategy to practical reality  
        3. **Respekt för Tid**: Deliver maximum value in minimal time (<10 minutes)
        4. **Helhetssyn Genom Handling**: Teach systems thinking through interaction
        5. **Intelligens Inte Infantilisering**: Maintain professional sophistication
        """

    def _run(self, specification_text: str) -> str:
        """Validate specification against design principles."""
        try:
            if not self.claude_llm:
                return self._fallback_validation(specification_text)

            # Load design principles
            principles_content = self._load_design_principles()

            # Create validation prompt
            prompt = f"""
            You are a Senior UX Design Validator for DigiNativa, a learning game for Swedish public sector digitalization.

            DESIGN PRINCIPLES TO VALIDATE AGAINST:
            {principles_content}

            SPECIFICATION TO REVIEW:
            {specification_text}

            TASK: Evaluate this specification against each of the 5 design principles.

            For each principle, provide:
            - Score: 1-5 (1=poor, 5=excellent)
            - Reasoning: Specific explanation with examples from the specification

            CRITICAL: Respond ONLY with valid JSON in this exact format:
            {{
                "principle_1_pedagogy": {{
                    "score": <int 1-5>,
                    "reasoning": "<specific reasoning with examples>"
                }},
                "principle_2_policy_to_practice": {{
                    "score": <int 1-5>,
                    "reasoning": "<specific reasoning with examples>"
                }},
                "principle_3_time_respect": {{
                    "score": <int 1-5>,
                    "reasoning": "<specific reasoning with examples>"
                }},
                "principle_4_holistic_view": {{
                    "score": <int 1-5>,
                    "reasoning": "<specific reasoning with examples>"
                }},
                "principle_5_intelligence_not_infantilization": {{
                    "score": <int 1-5>,
                    "reasoning": "<specific reasoning with examples>"
                }},
                "overall_score": <float 0.0-1.0>,
                "validation_summary": "<brief overall assessment>"
            }}

            Focus on Swedish public sector context and "Anna" persona needs.
            """

            # Get validation from Claude
            response = self.claude_llm.invoke(prompt)
            
            # Parse and validate JSON response
            try:
                validation_data = json.loads(response.content)
                
                # Calculate overall score if not provided
                if "overall_score" not in validation_data:
                    scores = [
                        validation_data.get("principle_1_pedagogy", {}).get("score", 3),
                        validation_data.get("principle_2_policy_to_practice", {}).get("score", 3),
                        validation_data.get("principle_3_time_respect", {}).get("score", 3),
                        validation_data.get("principle_4_holistic_view", {}).get("score", 3),
                        validation_data.get("principle_5_intelligence_not_infantilization", {}).get("score", 3)
                    ]
                    validation_data["overall_score"] = sum(scores) / len(scores) / 5.0
                
                return json.dumps(validation_data, ensure_ascii=False, indent=2)
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Invalid JSON from Claude: {e}")
                return self._fallback_validation(specification_text)
            
        except Exception as e:
            print(f"⚠️  Design validation error: {e}")
            return self._fallback_validation(specification_text)

    def _fallback_validation(self, specification_text: str) -> str:
        """Fallback validation when Claude is not available."""
        return json.dumps({
            "principle_1_pedagogy": {
                "score": 3,
                "reasoning": "Manual review required - AI validation unavailable"
            },
            "principle_2_policy_to_practice": {
                "score": 3,
                "reasoning": "Manual review required - AI validation unavailable"
            },
            "principle_3_time_respect": {
                "score": 3,
                "reasoning": "Manual review required - AI validation unavailable"
            },
            "principle_4_holistic_view": {
                "score": 3,
                "reasoning": "Manual review required - AI validation unavailable"
            },
            "principle_5_intelligence_not_infantilization": {
                "score": 3,
                "reasoning": "Manual review required - AI validation unavailable"
            },
            "overall_score": 0.6,
            "validation_summary": "Fallback validation - manual review required",
            "fallback_mode": True
        }, ensure_ascii=False, indent=2)


class AcceptanceCriteriaValidatorTool(BaseTool):
    """
    Tool for validating acceptance criteria to ensure they are specific, 
    measurable, and testable according to DigiNativa quality standards.
    """
    name: str = "Acceptance Criteria Validator"
    description: str = (
        "Validate acceptance criteria to ensure they are specific, measurable, testable, "
        "and aligned with DigiNativa's quality standards. Returns validation results "
        "with improvement suggestions for unclear criteria."
    )
    args_schema: Type[BaseModel] = AcceptanceCriteriaInput
    claude_llm: Optional[ChatAnthropic] = None # KORRIGERING: Fältet är tillagt

    
    def __init__(self):
        super().__init__()
        self.claude_llm = self._create_claude_llm()

    def _create_claude_llm(self) -> Optional[ChatAnthropic]:
        """Create Claude LLM instance with error handling."""
        try:
            api_key = SECRETS.get("anthropic_api_key")
            if not api_key or api_key.startswith("[YOUR_"):
                return None
                
            return ChatAnthropic(
                model=AGENT_CONFIG["llm_model"],
                api_key=api_key,
                temperature=0.1,
                max_tokens_to_sample=2000
            )
        except Exception as e:
            print(f"⚠️  Could not initialize Claude LLM for criteria validation: {e}")
            return None

    def _run(self, criteria_list: List[str]) -> str:
        """Validate acceptance criteria for testability and clarity."""
        try:
            if not self.claude_llm:
                return self._fallback_criteria_validation(criteria_list)

            # Create validation prompt
            criteria_text = "\n".join([f"{i+1}. {criterion}" for i, criterion in enumerate(criteria_list)])
            
            prompt = f"""
            You are a QA Lead expert in writing testable requirements for DigiNativa learning game development.

            ACCEPTANCE CRITERIA TO VALIDATE:
            {criteria_text}

            VALIDATION STANDARDS:
            - Specific: Clear and unambiguous
            - Measurable: Has quantifiable success metrics
            - Testable: Can be verified through testing
            - Relevant: Serves Anna's needs (busy public sector professional)
            - Time-bound: Includes performance expectations

            TASK: For each criterion, determine if it meets quality standards.

            CRITICAL: Respond ONLY with valid JSON array in this exact format:
            [
                {{
                    "criterion": "<original criterion text>",
                    "is_testable": <boolean>,
                    "is_specific": <boolean>,
                    "is_measurable": <boolean>,
                    "overall_quality": "<poor|fair|good|excellent>",
                    "improvement_suggestion": "<specific improvement or empty string>",
                    "test_approach": "<how this could be tested>"
                }}
            ]

            Focus on DigiNativa context: professional learning game for Swedish public sector.
            """

            # Get validation from Claude
            response = self.claude_llm.invoke(prompt)
            
            # Parse and validate JSON response
            try:
                validation_data = json.loads(response.content)
                return json.dumps(validation_data, ensure_ascii=False, indent=2)
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Invalid JSON from Claude: {e}")
                return self._fallback_criteria_validation(criteria_list)
            
        except Exception as e:
            print(f"⚠️  Criteria validation error: {e}")
            return self._fallback_criteria_validation(criteria_list)

    def _fallback_criteria_validation(self, criteria_list: List[str]) -> str:
        """Fallback validation when Claude is not available."""
        fallback_results = []
        
        for criterion in criteria_list:
            # Simple heuristic validation
            is_specific = len(criterion.split()) > 5  # Has enough detail
            is_measurable = any(word in criterion.lower() for word in 
                              ['%', 'seconds', 'minutes', 'score', 'count', 'number', 'within', '<', '>', 'exactly'])
            is_testable = any(word in criterion.lower() for word in 
                            ['can', 'should', 'displays', 'shows', 'works', 'loads', 'saves'])
            
            overall_quality = "good" if (is_specific and is_measurable and is_testable) else "fair"
            
            fallback_results.append({
                "criterion": criterion,
                "is_testable": is_testable,
                "is_specific": is_specific,
                "is_measurable": is_measurable,
                "overall_quality": overall_quality,
                "improvement_suggestion": "Manual review recommended - AI validation unavailable",
                "test_approach": "Determine appropriate testing method manually"
            })
        
        return json.dumps(fallback_results, ensure_ascii=False, indent=2)


class AnnaPersonaValidatorTool(BaseTool):
    """
    Tool for validating designs against the "Anna" persona - the primary target user
    for DigiNativa. Ensures all design decisions serve a busy public sector professional.
    """
    name: str = "Anna Persona Validator"
    description: str = (
        "Validate designs against the 'Anna' persona - a 42-year-old IT strategist "
        "in Swedish public sector. Ensures designs meet her needs for professional, "
        "time-efficient, and pedagogically effective learning experiences."
    )
    args_schema: Type[BaseModel] = DesignValidationInput
    claude_llm: Optional[ChatAnthropic] = None
    anna_profile: Optional[str] = None
    
    def __init__(self):
        super().__init__()
        self.claude_llm = self._create_claude_llm()
        self.anna_profile = self._load_anna_profile()

    def _create_claude_llm(self) -> Optional[ChatAnthropic]:
        """Create Claude LLM instance with error handling."""
        try:
            api_key = SECRETS.get("anthropic_api_key")
            if not api_key or api_key.startswith("[YOUR_"):
                return None
                
            return ChatAnthropic(
                model=AGENT_CONFIG["llm_model"],
                api_key=api_key,
                temperature=0.2,  # Slightly higher for persona understanding
                max_tokens_to_sample=2000
            )
        except Exception as e:
            print(f"⚠️  Could not initialize Claude LLM for persona validation: {e}")
            return None

    def _load_anna_profile(self) -> str:
        """Load Anna persona profile from DNA documents."""
        try:
            target_audience_path = DNA_DIR / "target_audience.md"
            if target_audience_path.exists():
                return read_file(str(target_audience_path), agent_name="persona_validator")
            else:
                return self._get_default_anna_profile()
        except Exception as e:
            print(f"⚠️  Could not load Anna profile: {e}")
            return self._get_default_anna_profile()

    def _get_default_anna_profile(self) -> str:
        """Default Anna profile if DNA document is not available."""
        return """
        # Primary Persona: "Anna" Svensson
        
        - Age: 42, IT-strategist/Digital utvecklingschef
        - Location: Mellanstor svensk kommun  
        - Experience: 8 år inom offentlig förvaltning
        - Time constraints: <10 minuter per session
        - Technical level: Intermediate
        - Goals: Professional development, practical skills, efficiency
        - Pain points: Time pressure, complexity, unclear value
        """

    def _run(self, specification_text: str) -> str:
        """Validate specification against Anna persona needs."""
        try:
            if not self.claude_llm:
                return self._fallback_persona_validation()

            prompt = f"""
            You are a UX researcher specializing in public sector user experience.

            ANNA PERSONA PROFILE:
            {self.anna_profile}

            DESIGN SPECIFICATION TO EVALUATE:
            {specification_text}

            TASK: Evaluate how well this design serves Anna's specific needs and constraints.

            Consider these Anna-specific factors:
            - Professional context and responsibilities
            - Time constraints and busy schedule
            - Technical comfort level
            - Learning preferences and motivations
            - Pain points and frustrations
            - Swedish public sector culture

            CRITICAL: Respond ONLY with valid JSON in this exact format:
            {{
                "anna_alignment_score": <float 0.0-1.0>,
                "time_respect": {{
                    "score": <int 1-5>,
                    "reasoning": "<how design respects Anna's time constraints>"
                }},
                "professional_tone": {{
                    "score": <int 1-5>,
                    "reasoning": "<how design maintains professional sophistication>"
                }},
                "practical_value": {{
                    "score": <int 1-5>,
                    "reasoning": "<how design provides immediate practical value>"
                }},
                "usability": {{
                    "score": <int 1-5>,
                    "reasoning": "<how easy design is for Anna to use>"
                }},
                "recommendations": [
                    "<specific recommendation for improving Anna alignment>",
                    "<another recommendation>"
                ],
                "validation_summary": "<overall assessment from Anna's perspective>"
            }}
            """

            response = self.claude_llm.invoke(prompt)
            
            try:
                validation_data = json.loads(response.content)
                return json.dumps(validation_data, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                return self._fallback_persona_validation()
            
        except Exception as e:
            print(f"⚠️  Anna persona validation error: {e}")
            return self._fallback_persona_validation()

    def _fallback_persona_validation(self) -> str:
        """Fallback validation when Claude is not available."""
        return json.dumps({
            "anna_alignment_score": 0.7,
            "time_respect": {
                "score": 3,
                "reasoning": "Manual review required for time constraint assessment"
            },
            "professional_tone": {
                "score": 3,
                "reasoning": "Manual review required for professional tone assessment"
            },
            "practical_value": {
                "score": 3,
                "reasoning": "Manual review required for practical value assessment"
            },
            "usability": {
                "score": 3,
                "reasoning": "Manual review required for usability assessment"
            },
            "recommendations": [
                "Conduct manual Anna persona review",
                "Validate time constraints manually",
                "Check professional tone and terminology"
            ],
            "validation_summary": "Manual persona validation required - AI validation unavailable"
        }, ensure_ascii=False, indent=2)


# Convenience function for testing all design tools
def test_all_design_tools():
    """Test all design tools with sample data."""
    print("🧪 Testing DigiNativa Design Tools...")
    
    # Sample specification text
    sample_spec = """
    # User Progress Tracking Interface
    
    This feature allows Anna to view her learning progress through a clean,
    professional dashboard. The interface displays completion percentage,
    completed topics, and time invested in learning.
    
    Visual Design:
    - Professional blue color scheme (#0066CC)
    - Clean typography with good contrast
    - Card-based layout responsive to mobile
    
    Interactions:
    - Progress bar shows percentage completion
    - Clickable topic list with checkmarks
    - Quick access to continue learning
    - Loads in under 2 seconds
    """
    
    # Sample acceptance criteria
    sample_criteria = [
        "Progress bar displays completion percentage accurately",
        "Interface loads within 2 seconds",
        "All text is readable on mobile devices",
        "User can click to continue learning",
        "Design looks professional"
    ]
    
    try:
        # Test Design Principles Validator
        print("\n📊 Testing Design Principles Validator...")
        principles_validator = DesignPrinciplesValidatorTool()
        principles_result = principles_validator._run(sample_spec)
        print("✅ Design Principles validation completed")
        
        # Test Acceptance Criteria Validator
        print("\n📋 Testing Acceptance Criteria Validator...")
        criteria_validator = AcceptanceCriteriaValidatorTool()
        criteria_result = criteria_validator._run(sample_criteria)
        print("✅ Acceptance Criteria validation completed")
        
        # Test Anna Persona Validator
        print("\n👤 Testing Anna Persona Validator...")
        persona_validator = AnnaPersonaValidatorTool()
        persona_result = persona_validator._run(sample_spec)
        print("✅ Anna Persona validation completed")
        
        print("\n🎉 All design tools tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Design tools test failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests when module is executed directly
    test_all_design_tools()