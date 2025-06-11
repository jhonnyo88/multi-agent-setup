# DNA Documentation Guide

*How Project DNA Documents Work Together to Create Team Coherence*

---

## 🧬 **UNDERSTANDING PROJECT DNA**

### **What is Project DNA?**

Project DNA is the **shared decision-making framework** that ensures all AI agents work cohesively toward the same goals. It's not just documentation—it's the automated coordination system that prevents team fragmentation.

**Critical Concept:** DNA prevents the "telephone game" effect where each agent interprets requirements differently, leading to a fragmented final product.

### **DNA as Automated Decision Framework**

```python
# How every agent uses DNA for decisions
def make_agent_decision(options: List[Any], agent_type: str) -> Any:
    # 1. Filter by Design Principles (pedagogical value, time respect, etc.)
    principle_compliant = [opt for opt in options if validates_design_principles(opt)]
    
    # 2. Apply Architecture Constraints (API-first, stateless, etc.)
    architecture_compliant = [opt for opt in principle_compliant if follows_architecture(opt)]
    
    # 3. Check Game Design Document alignment
    gdd_aligned = [opt for opt in architecture_compliant if aligns_with_gdd(opt)]
    
    # 4. Validate component library usage
    component_compliant = [opt for opt in gdd_aligned if uses_component_library(opt)]
    
    # 5. Choose simplest solution (KISS principle)
    return choose_simplest_solution(component_compliant)
```

---

## 📚 **DNA DOCUMENT HIERARCHY**

### **Tier 1: Foundation Documents (Critical for All Decisions)**

#### **1. `design_principles.md` - The Decision Framework**

**Function:** Provides the 5 core criteria for ALL feature-level decisions.

**Structure:**
```markdown
# Design Principles

## 1. Pedagogik Framför Allt (Pedagogy First)
- Every element serves learning objectives
- Implementation guidance for each agent type
- Success metrics and validation criteria

## 2. Från Policy till Praktik (Policy to Practice)
- Connect abstract strategy to practical reality
- Agent-specific implementation patterns
- Real-world validation requirements

## 3. Respekt för Tid (Time Respect)
- Maximum value in minimal time
- Time constraint enforcement mechanisms
- Efficiency measurement criteria

## 4. Helhetssyn Genom Handling (Holistic Understanding)
- Learn systems thinking through action
- Integration requirements between components
- Systems-level validation approaches

## 5. Intelligens, Inte Infantilisering (Intelligence, Not Infantilization)
- Professional tone and sophistication
- Complexity management guidelines
- User respect validation methods
```

**Agent Usage Pattern:**
```python
# Every agent decision validates against all 5 principles
def validate_against_design_principles(proposal: Any) -> Dict[str, bool]:
    return {
        "pedagogical_value": validates_principle_1(proposal),
        "policy_to_practice": validates_principle_2(proposal),
        "time_respect": validates_principle_3(proposal),
        "holistic_thinking": validates_principle_4(proposal),
        "professional_tone": validates_principle_5(proposal)
    }

# Block decisions that fail multiple principles
if sum(validation_results.values()) < 4:  # At least 4 of 5 must pass
    raise DesignPrincipleViolationError("Proposal fails design principles")
```

#### **2. `architecture.md` - Technical Constraints**

**Function:** Defines non-negotiable technical patterns that ensure system coherence.

**Structure:**
```markdown
# Architecture

## 1. Separation of Concerns
- Frontend handles presentation only
- Backend handles business logic only
- Communication via APIs only

## 2. API-First Design
- All communication via REST JSON APIs
- No direct database calls from frontend
- Stateless request/response patterns

## 3. Stateless Backend
- All state passed from client in requests
- No server-side session management
- Perfect for serverless deployment

## 4. Simplicity First (KISS)
- Choose simplest solution that works
- Optimize only when measurements show need
- Document why complex solutions were chosen
```

**Agent Usage Pattern:**
```python
# Architecture validation for technical decisions
def validate_architecture_compliance(code_design: Any) -> Dict[str, bool]:
    return {
        "api_first": validates_api_first_design(code_design),
        "stateless_backend": validates_stateless_pattern(code_design),
        "separation_of_concerns": validates_separation(code_design),
        "simplicity_first": validates_kiss_principle(code_design)
    }

# Architecture violations are non-negotiable failures
if not all(architecture_validation.values()):
    raise ArchitectureViolationError("Code violates architecture principles")
```

### **Tier 2: Product Vision Documents (Guide Implementation Details)**

#### **3. `game_design_document.md` - Complete Product Blueprint**

**Function:** Comprehensive product vision that all agents reference for implementation alignment.

**Structure:**
```markdown
# Game Design Document (GDD)

## Core Game Loop
- Primary player actions and feedback cycles
- Learning objective integration points
- Progress and achievement systems

## Detailed Game Mechanics
- Specific interaction patterns
- Challenge progression systems
- Knowledge validation approaches

## User Experience Flow
- Complete user journey from start to mastery
- Decision points and branching narratives
- Error recovery and help systems

## Content Structure
- Learning modules and their relationships
- Assessment and reflection integration
- Real-world application connections

## Technical Requirements
- Performance specifications
- Platform compatibility requirements
- Integration with component libraries
```

**Agent Usage Pattern:**
```python
# GDD alignment validation
def validate_gdd_alignment(feature_design: Any) -> bool:
    gdd_sections = load_gdd_document()
    
    # Check if feature aligns with documented game mechanics
    mechanics_alignment = feature_design.aligns_with(gdd_sections["game_mechanics"])
    
    # Check if feature supports documented user journey
    journey_support = feature_design.supports(gdd_sections["user_experience_flow"])
    
    # Check if feature serves documented learning objectives
    learning_alignment = feature_design.serves(gdd_sections["learning_objectives"])
    
    return all([mechanics_alignment, journey_support, learning_alignment])
```

#### **4. `component_library.md` - Implementation Standards**

**Function:** Ensures consistent UI/UX implementation across all features.

**Structure:**
```markdown
# Component Library Standards

## Shadcn/UI Components
- Available components and usage patterns
- Customization guidelines and limitations
- Accessibility implementation requirements

## Kenney.UI Game Assets
- Available asset categories and specifications
- Usage guidelines for game UI elements
- Integration patterns with Shadcn components

## Custom Component Standards
- When to create custom components
- Naming conventions and file organization
- Documentation and testing requirements

## Responsive Design Requirements
- Breakpoint definitions and behavior
- Mobile-first design principles
- Touch interaction guidelines

## Accessibility Standards
- WCAG compliance requirements
- Screen reader compatibility patterns
- Keyboard navigation specifications
```

**Agent Usage Pattern:**
```python
# Component library compliance validation
def validate_component_usage(ui_specification: Any) -> Dict[str, bool]:
    component_library = load_component_library_standards()
    
    return {
        "uses_approved_components": ui_specification.uses_only(
            component_library["approved_components"]
        ),
        "follows_responsive_patterns": ui_specification.implements(
            component_library["responsive_requirements"]
        ),
        "meets_accessibility_standards": ui_specification.complies_with(
            component_library["accessibility_standards"]
        ),
        "follows_naming_conventions": ui_specification.follows(
            component_library["naming_conventions"]
        )
    }
```

#### **5. `target_audience.md` - User Context and Personas**

**Function:** Provides deep understanding of user needs and context for all design decisions.

**Structure:**
```markdown
# Target Audience

## Primary Persona: Anna
- Role: Public sector employee in Swedish municipality
- Background: Non-technical but intelligent professional
- Goals: Learn digitalization strategy for practical application
- Constraints: Limited time, needs immediate practical value
- Context: Workplace learning during busy workday

## Secondary Personas
- Municipal leadership (strategic oversight)
- IT coordinators (technical implementation)
- Citizen service representatives (frontline application)

## User Context
- Swedish public sector digitalization challenges
- Current tools and systems in use
- Organizational constraints and opportunities
- Success metrics and evaluation criteria

## Usage Scenarios
- Quick learning sessions during breaks
- Preparation for strategy meetings
- Reference during implementation projects
- Team training and discussion facilitation
```

**Agent Usage Pattern:**
```python
# Target audience validation
def validate_target_audience_fit(design_decision: Any) -> Dict[str, bool]:
    anna_persona = load_target_audience()["primary_persona"]
    
    return {
        "appropriate_for_skill_level": design_decision.matches_skill_level(
            anna_persona["technical_background"]
        ),
        "respects_time_constraints": design_decision.completion_time <= 
            anna_persona["available_time_minutes"],
        "serves_professional_goals": design_decision.advances(
            anna_persona["learning_objectives"]
        ),
        "fits_usage_context": design_decision.works_in(
            anna_persona["work_environment"]
        )
    }
```

---

## 🔗 **HOW DNA DOCUMENTS WORK TOGETHER**

### **Decision Flow Example: Adding a New Feature**

```
1. PROJECT MANAGER receives feature request
   ↓
   Validates against design_principles.md (all 5 principles)
   Checks target_audience.md (Anna persona fit)
   References game_design_document.md (GDD alignment)
   ↓
   Creates story breakdown with DNA compliance requirements

2. GAME DESIGNER receives story
   ↓
   Designs mechanics using design_principles.md (pedagogical value)
   Follows game_design_document.md (core game loop)
   Specifies UI using component_library.md (Shadcn/UI + Kenney.UI)
   Validates against target_audience.md (Anna's needs)
   ↓
   Creates game design + UX specification with DNA compliance

3. DEVELOPER receives specification
   ↓
   Implements following architecture.md (API-first, stateless)
   Uses component_library.md (approved components only)
   Maintains design_principles.md (simplicity, professionalism)
   ↓
   Creates working code with architecture compliance

4. All subsequent agents (Test Engineer, QA Tester, Quality Reviewer)
   ↓
   Validate all work against complete DNA framework
   Ensure end-to-end consistency and quality
```

### **DNA Consistency Enforcement**

```python
class DNAConsistencyChecker:
    """
    Ensures all agents maintain DNA consistency throughout development.
    
    PURPOSE:
    Prevents DNA drift where agents gradually deviate from project principles.
    """
    
    def __init__(self):
        self.dna_documents = self._load_all_dna_docs()
        self.consistency_scores = {}
    
    def check_story_dna_consistency(self, story_id: str) -> Dict[str, float]:
        """
        Check DNA consistency across all artifacts for a story.
        
        Returns consistency scores for each DNA document (0.0 to 1.0).
        """
        story_artifacts = self._collect_story_artifacts(story_id)
        
        consistency_scores = {}
        
        # Check design principles consistency
        consistency_scores["design_principles"] = self._check_design_principles_consistency(
            story_artifacts
        )
        
        # Check architecture consistency
        consistency_scores["architecture"] = self._check_architecture_consistency(
            story_artifacts
        )
        
        # Check GDD alignment consistency
        consistency_scores["gdd_alignment"] = self._check_gdd_consistency(
            story_artifacts
        )
        
        # Check component library consistency
        consistency_scores["component_library"] = self._check_component_consistency(
            story_artifacts
        )
        
        # Check target audience consistency
        consistency_scores["target_audience"] = self._check_audience_consistency(
            story_artifacts
        )
        
        return consistency_scores
    
    def detect_dna_drift(self, recent_stories: List[str]) -> Dict[str, Any]:
        """
        Detect if team is drifting from DNA principles over time.
        
        Returns drift analysis and recommended corrections.
        """
        drift_analysis = {
            "overall_drift_score": 0.0,
            "drifting_principles": [],
            "consistency_trends": {},
            "recommended_actions": []
        }
        
        # Analyze consistency trends across recent stories
        for story_id in recent_stories:
            story_consistency = self.check_story_dna_consistency(story_id)
            
            for principle, score in story_consistency.items():
                if principle not in drift_analysis["consistency_trends"]:
                    drift_analysis["consistency_trends"][principle] = []
                
                drift_analysis["consistency_trends"][principle].append(score)
        
        # Calculate overall drift and identify problems
        for principle, scores in drift_analysis["consistency_trends"].items():
            avg_score = sum(scores) / len(scores)
            
            if avg_score < 0.8:  # Below 80% consistency
                drift_analysis["drifting_principles"].append(principle)
                drift_analysis["recommended_actions"].append(
                    f"Review and reinforce {principle} guidelines with team"
                )
        
        # Calculate overall drift score
        all_scores = [score for scores in drift_analysis["consistency_trends"].values() 
                     for score in scores]
        drift_analysis["overall_drift_score"] = sum(all_scores) / len(all_scores)
        
        return drift_analysis
    
    def _load_all_dna_docs(self) -> Dict[str, Any]:
        """Load all DNA documents for consistency checking."""
        # Implementation would parse all DNA markdown files
        return {
            "design_principles": {},
            "architecture": {},
            "game_design_document": {},
            "component_library": {},
            "target_audience": {}
        }
    
    def _collect_story_artifacts(self, story_id: str) -> Dict[str, Any]:
        """Collect all artifacts created for