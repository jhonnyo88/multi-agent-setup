# Agent Contracts Reference Guide

*Detailed specifications for all agent-to-agent contracts in the DigiNativa AI Team*

---

## 📋 **CONTRACT VALIDATION FRAMEWORK**

### **Contract Schema Definition**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AI Team Agent Contract Schema",
  "type": "object",
  "required": [
    "contract_version",
    "story_id", 
    "source_agent",
    "target_agent",
    "dna_compliance",
    "input_requirements",
    "output_specifications"
  ],
  "properties": {
    "contract_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Semantic version for contract compatibility"
    },
    "story_id": {
      "type": "string",
      "pattern": "^STORY-[0-9]+-[0-9]+$",
      "description": "Unique identifier linking to feature and increment"
    },
    "source_agent": {
      "enum": ["project_manager", "game_designer", "developer", "test_engineer", "qa_tester", "quality_reviewer"],
      "description": "Agent providing the work"
    },
    "target_agent": {
      "enum": ["project_manager", "game_designer", "developer", "test_engineer", "qa_tester", "quality_reviewer"],
      "description": "Agent receiving the work"
    },
    "dna_compliance": {
      "type": "object",
      "required": ["design_principles_validation", "architecture_compliance"],
      "properties": {
        "design_principles_validation": {
          "type": "object",
          "properties": {
            "pedagogical_value": {"type": "boolean"},
            "policy_to_practice": {"type": "boolean"},
            "time_respect": {"type": "boolean"},
            "holistic_thinking": {"type": "boolean"},
            "professional_tone": {"type": "boolean"}
          },
          "additionalProperties": false
        },
        "architecture_compliance": {
          "type": "object",
          "properties": {
            "api_first": {"type": "boolean"},
            "stateless_backend": {"type": "boolean"},
            "separation_of_concerns": {"type": "boolean"},
            "simplicity_first": {"type": "boolean"}
          },
          "additionalProperties": false
        }
      }
    },
    "input_requirements": {
      "type": "object",
      "required": ["required_files", "required_data", "required_validations"],
      "properties": {
        "required_files": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Files that must exist before handoff"
        },
        "required_data": {
          "type": "object",
          "description": "Data structures that must be present"
        },
        "required_validations": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Validation checks that must pass"
        }
      }
    },
    "output_specifications": {
      "type": "object",
      "required": ["deliverable_files", "deliverable_data", "validation_criteria"],
      "properties": {
        "deliverable_files": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Files that must be created"
        },
        "deliverable_data": {
          "type": "object",
          "description": "Data structures that must be provided"
        },
        "validation_criteria": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Criteria for validating output quality"
        }
      }
    },
    "quality_gates": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Automated checks that must pass"
    },
    "handoff_criteria": {
      "type": "array", 
      "items": {"type": "string"},
      "description": "Conditions for successful handoff"
    },
    "rollback_conditions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Conditions that trigger rollback"
    }
  }
}
```

---

## 🔗 **DETAILED CONTRACT SPECIFICATIONS**

### **1. Project Manager → Game Designer**

**Purpose:** Transform feature request into game design + UX specification

```json
{
  "contract_version": "1.0",
  "contract_type": "feature_to_game_design_and_ux",
  "description": "Project Manager hands off analyzed feature to Game Designer for both game mechanics design and UX specification",
  
  "input_requirements": {
    "required_files": [
      "docs/stories/story_description_{story_id}.md",
      "docs/analysis/feature_analysis_{feature_id}.json"
    ],
    "required_data": {
      "feature_description": "string",
      "acceptance_criteria": ["string"],
      "user_persona": "Anna",
      "time_constraint_minutes": "number",
      "learning_objectives": ["string"],
      "gdd_section_reference": "string",
      "priority_level": "string",
      "complexity_assessment": "object"
    },
    "required_validations": [
      "dna_design_principles_alignment_verified",
      "gdd_consistency_checked",
      "technical_feasibility_confirmed",
      "learning_objectives_clarity_validated"
    ]
  },
  
  "output_specifications": {
    "deliverable_files": [
      "docs/specs/game_design_{story_id}.md",
      "docs/specs/ux_specification_{story_id}.md",
      "docs/specs/component_mapping_{story_id}.json",
      "docs/specs/wireframes_{story_id}.png",
      "docs/specs/interaction_flow_{story_id}.json"
    ],
    "deliverable_data": {
      "game_mechanics": {
        "core_mechanic": "string",
        "player_actions": ["string"],
        "feedback_loops": ["object"],
        "progression_system": "object",
        "challenge_difficulty": "object"
      },
      "learning_design": {
        "pedagogical_approach": "string",
        "knowledge_checks": ["object"],
        "reflection_points": ["string"],
        "practical_applications": ["string"]
      },
      "ui_components": {
        "shadcn_components": ["string"],
        "custom_components": ["string"],
        "component_props": ["object"]
      },
      "game_assets": {
        "kenney_ui_elements": ["string"],
        "custom_assets_needed": ["string"],
        "asset_specifications": ["object"]
      },
      "interaction_flow": {
        "user_journey": ["object"],
        "decision_points": ["object"],
        "error_states": ["object"],
        "success_states": ["object"]
      },
      "responsive_design": {
        "breakpoints": ["string"],
        "mobile_adaptations": ["string"],
        "accessibility_features": ["string"]
      }
    },
    "validation_criteria": [
      "all_5_design_principles_addressed_in_game_mechanics",
      "learning_objectives_mapped_to_game_interactions",
      "component_library_compliance_verified",
      "mobile_responsiveness_specified",
      "accessibility_requirements_defined",
      "time_constraint_feasibility_confirmed"
    ]
  },
  
  "quality_gates": [
    "game_mechanics_pedagogical_value_validation",
    "wireframe_clarity_and_completeness_check",
    "component_availability_in_libraries_verification",
    "interaction_flow_logical_consistency_validation",
    "accessibility_compliance_preliminary_check"
  ],
  
  "handoff_criteria": [
    "game_design_document_completeness",
    "ux_specification_implementation_clarity",
    "component_mapping_accuracy_and_availability",
    "wireframes_developer_comprehensibility",
    "interaction_flow_unambiguous_definition"
  ],
  
  "rollback_conditions": [
    "game_mechanics_do_not_serve_learning_objectives",
    "ux_specification_violates_architecture_principles",
    "required_components_not_available_in_libraries",
    "time_constraint_cannot_be_met_with_design",
    "accessibility_requirements_cannot_be_satisfied"
  ]
}
```

### **2. Game Designer → Developer**

**Purpose:** Transform game design + UX specification into working code

```json
{
  "contract_version": "1.0",
  "contract_type": "game_design_and_ux_to_implementation",
  "description": "Game Designer hands off complete design to Developer for full-stack implementation",
  
  "input_requirements": {
    "required_files": [
      "docs/specs/game_design_{story_id}.md",
      "docs/specs/ux_specification_{story_id}.md",
      "docs/specs/component_mapping_{story_id}.json",
      "docs/specs/wireframes_{story_id}.png",
      "docs/specs/interaction_flow_{story_id}.json"
    ],
    "required_data": {
      "game_mechanics": "object",
      "learning_design": "object",
      "ui_components": "object",
      "game_assets": "object",
      "interaction_flow": "object",
      "api_design": "object",
      "data_models": "object",
      "business_logic_rules": "object"
    },
    "required_validations": [
      "game_design_completeness_verified",
      "ux_specification_implementation_clarity_confirmed",
      "component_availability_checked",
      "api_design_architecture_compliance_validated"
    ]
  },
  
  "output_specifications": {
    "deliverable_files": [
      "frontend/src/components/game/{ComponentName}.tsx",
      "frontend/src/components/ui/{UIComponentName}.tsx",
      "frontend/src/pages/game/{PageName}.tsx",
      "frontend/src/hooks/useGame{HookName}.ts",
      "frontend/src/types/game.types.ts",
      "backend/src/routes/game/{route_name}.py",
      "backend/src/models/game/{model_name}.py",
      "backend/src/services/game/{service_name}.py",
      "backend/tests/test_game_{feature_name}.py",
      "frontend/src/tests/game/{ComponentName}.test.tsx"
    ],
    "deliverable_data": {
      "api_endpoints": {
        "endpoints": ["object"],
        "request_schemas": ["object"],
        "response_schemas": ["object"],
        "error_handling": ["object"]
      },
      "frontend_components": {
        "component_interfaces": ["object"],
        "prop_definitions": ["object"],
        "state_management": "object",
        "event_handling": ["object"]
      },
      "game_state_management": {
        "state_structure": "object",
        "state_transitions": ["object"],
        "persistence_strategy": "string"
      },
      "integration_points": {
        "api_integration": ["object"],
        "component_communication": ["object"],
        "error_boundaries": ["object"]
      }
    },
    "validation_criteria": [
      "all_game_mechanics_implemented_correctly",
      "architecture_principles_followed_throughout",
      "component_library_used_appropriately",
      "api_first_design_implemented",
      "stateless_backend_maintained",
      "responsive_design_achieved"
    ]
  },
  
  "quality_gates": [
    "typescript_compilation_success_zero_errors",
    "eslint_standards_compliance_verified",
    "api_response_time_under_200ms_confirmed",
    "mobile_responsiveness_validated",
    "accessibility_initial_compliance_checked"
  ],
  
  "handoff_criteria": [
    "all_game_mechanics_functionally_complete",
    "ui_matches_wireframes_and_specifications",
    "api_endpoints_respond_correctly",
    "component_integration_working",
    "error_handling_implemented_comprehensively"
  ],
  
  "rollback_conditions": [
    "critical_game_mechanics_not_implementable",
    "performance_requirements_cannot_be_met",
    "architecture_principles_violated",
    "component_library_integration_fails",
    "accessibility_requirements_not_achievable"
  ]
}
```

### **3. Developer → Test Engineer**

**Purpose:** Transform working code into comprehensive test suite

```json
{
  "contract_version": "1.0",
  "contract_type": "implementation_to_comprehensive_testing",
  "description": "Developer hands off working implementation to Test Engineer for automated testing",
  
  "input_requirements": {
    "required_files": [
      "frontend/src/components/game/*.tsx",
      "frontend/src/pages/game/*.tsx",
      "backend/src/routes/game/*.py",
      "backend/src/models/game/*.py",
      "backend/src/services/game/*.py"
    ],
    "required_data": {
      "api_endpoints_documentation": "object",
      "component_interfaces": "object",
      "game_mechanics_implementation": "object",
      "business_logic_flows": "object",
      "error_handling_patterns": "object"
    },
    "required_validations": [
      "code_compilation_successful",
      "basic_functionality_verified",
      "architecture_compliance_confirmed",
      "game_mechanics_working_as_designed"
    ]
  },
  
  "output_specifications": {
    "deliverable_files": [
      "tests/unit/game/test_{component_name}_unit.py",
      "tests/integration/game/test_{feature_name}_integration.py",
      "tests/e2e/game/test_{user_journey}_e2e.py",
      "tests/performance/game/test_{feature_name}_performance.py",
      "tests/accessibility/game/test_{feature_name}_a11y.py",
      "reports/test_coverage_{story_id}.html",
      "reports/performance_benchmarks_{story_id}.json"
    ],
    "deliverable_data": {
      "test_coverage_metrics": {
        "unit_test_coverage": "number",
        "integration_test_coverage": "number",
        "e2e_test_coverage": "number",
        "overall_coverage_percentage": "number"
      },
      "performance_metrics": {
        "api_response_times": ["object"],
        "frontend_load_times": ["object"],
        "memory_usage": ["object"],
        "lighthouse_scores": "object"
      },
      "accessibility_validation": {
        "wcag_compliance_level": "string",
        "screen_reader_compatibility": "boolean",
        "keyboard_navigation_support": "boolean",
        "color_contrast_validation": "object"
      },
      "game_mechanics_validation": {
        "learning_objective_achievement": ["object"],
        "user_interaction_flows": ["object"],
        "error_state_handling": ["object"]
      }
    },
    "validation_criteria": [
      "100_percent_unit_test_coverage_achieved",
      "all_automated_tests_pass_consistently",
      "performance_benchmarks_met_or_exceeded",
      "accessibility_standards_validated",
      "game_mechanics_thoroughly_tested"
    ]
  },
  
  "quality_gates": [
    "zero_test_failures_across_all_suites",
    "code_coverage_meets_100_percent_threshold",
    "performance_benchmarks_within_acceptable_ranges",
    "accessibility_compliance_verified",
    "security_vulnerability_scan_clean"
  ]
}
```

### **4. Test Engineer → QA Tester**

**Purpose:** Transform tested code into user experience validation

```json
{
  "contract_version": "1.0",
  "contract_type": "testing_to_user_validation",
  "description": "Test Engineer hands off tested implementation to QA Tester for user perspective validation",
  
  "input_requirements": {
    "required_files": [
      "tests/unit/game/*.py",
      "tests/integration/game/*.py",
      "tests/e2e/game/*.py",
      "reports/test_coverage_{story_id}.html",
      "reports/performance_benchmarks_{story_id}.json",
      "deployed_feature_preview_url"
    ],
    "required_data": {
      "test_results_summary": "object",
      "performance_validation": "object",
      "accessibility_compliance": "object",
      "feature_functionality_confirmation": "object"
    },
    "required_validations": [
      "all_automated_tests_passing",
      "performance_requirements_met",
      "feature_deployed_and_accessible",
      "basic_functionality_working"
    ]
  },
  
  "output_specifications": {
    "deliverable_files": [
      "qa_reports/{story_id}_user_experience_validation.md",
      "qa_reports/{story_id}_dna_compliance_assessment.json",
      "qa_reports/{story_id}_anna_persona_testing.md",
      "qa_reports/{story_id}_accessibility_user_testing.md",
      "qa_reports/{story_id}_learning_objectives_validation.md"
    ],
    "deliverable_data": {
      "user_experience_validation": {
        "anna_task_completion_success": "boolean",
        "task_completion_time_minutes": "number",
        "user_satisfaction_score": "number",
        "usability_issues_identified": ["string"]
      },
      "dna_principle_compliance": {
        "pedagogical_value_score": "number",
        "policy_to_practice_connection": "number",
        "time_respect_validation": "number",
        "holistic_thinking_promotion": "number",
        "professional_tone_maintenance": "number"
      },
      "anna_persona_validation": {
        "public_sector_relevance": "number",
        "digitalization_strategy_learning": "number",
        "practical_applicability": "number",
        "professional_context_appropriateness": "number"
      },
      "learning_outcomes_assessment": {
        "learning_objectives_met": ["boolean"],
        "knowledge_retention_potential": "number",
        "practical_application_likelihood": "number",
        "engagement_level_achieved": "number"
      }
    },
    "validation_criteria": [
      "anna_completes_task_under_10_minutes",
      "all_5_design_principles_validated_in_practice",
      "learning_objectives_demonstrably_achieved",
      "professional_tone_maintained_throughout",
      "accessibility_works_for_real_users"
    ]
  },
  
  "quality_gates": [
    "user_task_completion_success_rate_above_90_percent",
    "dna_compliance_scores_above_threshold",
    "accessibility_real_user_validation_passed",
    "learning_objectives_achievement_confirmed"
  ]
}
```

### **5. QA Tester → Quality Reviewer**

**Purpose:** Transform user-validated feature into production-ready deployment

```json
{
  "contract_version": "1.0",
  "contract_type": "user_validation_to_production_approval",
  "description": "QA Tester hands off user-validated feature to Quality Reviewer for final production approval",
  
  "input_requirements": {
    "required_files": [
      "qa_reports/{story_id}_user_experience_validation.md",
      "qa_reports/{story_id}_dna_compliance_assessment.json",
      "qa_reports/{story_id}_anna_persona_testing.md",
      "qa_reports/{story_id}_learning_objectives_validation.md",
      "complete_feature_implementation_in_production_environment"
    ],
    "required_data": {
      "qa_validation_results": "object",
      "user_testing_outcomes": "object",
      "dna_compliance_scores": "object",
      "learning_outcomes_validation": "object"
    },
    "required_validations": [
      "qa_validation_passed_all_criteria",
      "user_experience_validated_successfully",
      "dna_compliance_verified_in_practice",
      "feature_ready_for_production_evaluation"
    ]
  },
  
  "output_specifications": {
    "deliverable_files": [
      "quality_reports/{story_id}_final_production_approval.md",
      "quality_reports/{story_id}_performance_validation.json",
      "quality_reports/{story_id}_security_assessment.md",
      "deployment/{story_id}_release_notes.md",
      "deployment/{story_id}_rollback_plan.md"
    ],
    "deliverable_data": {
      "final_quality_assessment": {
        "overall_quality_score": "number",
        "production_readiness_confirmed": "boolean",
        "deployment_recommendation": "string",
        "risk_assessment": "object"
      },
      "performance_validation": {
        "lighthouse_score": "number",
        "core_web_vitals": "object",
        "api_performance_metrics": "object",
        "scalability_assessment": "object"
      },
      "security_validation": {
        "vulnerability_scan_results": "object",
        "security_best_practices_compliance": "boolean",
        "data_privacy_compliance": "boolean",
        "authentication_authorization_validation": "object"
      },
      "production_deployment_plan": {
        "deployment_strategy": "string",
        "rollback_procedures": ["string"],
        "monitoring_requirements": ["string"],
        "success_metrics": ["object"]
      }
    },
    "validation_criteria": [
      "lighthouse_score_above_90_all_categories",
      "zero_security_vulnerabilities_identified",
      "performance_benchmarks_met_under_load",
      "production_deployment_plan_comprehensive",
      "rollback_procedures_tested_and_verified"
    ]
  },
  
  "quality_gates": [
    "production_performance_requirements_validated",
    "security_compliance_fully_verified",
    "scalability_requirements_confirmed",
    "monitoring_and_alerting_configured",
    "disaster_recovery_procedures_documented"
  ],
  
  "handoff_criteria": [
    "feature_approved_for_production_deployment",
    "all_production_readiness_criteria_met",
    "deployment_and_rollback_plans_approved",
    "monitoring_configured_and_tested"
  ]
}
```

---

## 🛠️ **CONTRACT VALIDATION IMPLEMENTATION**

### **Python Contract Validator**

```python
import json
import jsonschema
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class ContractValidator:
    """
    Validates agent contracts against schema and business rules.
    
    PURPOSE:
    Ensures all agent handoffs follow strict contract specifications,
    preventing integration failures and maintaining system modularity.
    """
    
    def __init__(self, schema_path: str = "docs/contracts/agent_contract_schema.json"):
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.dna_validator = DNAValidator()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the contract JSON schema for validation."""
        with open(self.schema_path, 'r') as f:
            return json.load(f)
    
    def validate_contract_structure(self, contract: Dict[str, Any]) -> List[str]:
        """
        Validate contract against JSON schema.
        
        Returns list of validation errors (empty if valid).
        """
        try:
            jsonschema.validate(instance=contract, schema=self.schema)
            return []
        except jsonschema.ValidationError as e:
            return [f"Schema validation error: {e.message}"]
        except Exception as e:
            return [f"Contract validation failed: {str(e)}"]
    
    def validate_contract_business_rules(self, contract: Dict[str, Any]) -> List[str]:
        """
        Validate contract against business rules and DNA compliance.
        
        Returns list of business rule violations (empty if valid).
        """
        errors = []
        
        # Validate DNA compliance requirements
        dna_compliance = contract.get("dna_compliance", {})
        if not self._validate_dna_compliance(dna_compliance):
            errors.append("DNA compliance validation failed")
        
        # Validate agent sequence
        source_agent = contract.get("source_agent")
        target_agent = contract.get("target_agent")
        if not self._validate_agent_sequence(source_agent, target_agent):
            errors.append(f"Invalid agent sequence: {source_agent} → {target_agent}")
        
        # Validate file path consistency
        if not self._validate_file_paths(contract):
            errors.append("File path validation failed")
        
        return errors
    
    def validate_handoff_readiness(self, contract: Dict[str, Any], 
                                 actual_deliverables: Dict[str, Any]) -> List[str]:
        """
        Validate that actual deliverables meet contract requirements.
        
        Returns list of readiness issues (empty if ready for handoff).
        """
        errors = []
        
        # Check required files exist
        required_files = contract.get("input_requirements", {}).get("required_files", [])
        for file_path in required_files:
            if not Path(file_path).exists():
                errors.append(f"Required file missing: {file_path}")
        
        # Check required data present
        required_data = contract.get("input_requirements", {}).get("required_data", {})
        for data_key, data_type in required_data.items():
            if data_key not in actual_deliverables:
                errors.append(f"Required data missing: {data_key}")
        
        # Check quality gates
        quality_gates = contract.get("quality_gates", [])
        for gate in quality_gates:
            if not self._check_quality_gate(gate, actual_deliverables):
                errors.append(f"Quality gate failed: {gate}")
        
        return errors
    
    def _validate_dna_compliance(self, dna_compliance: Dict[str, Any]) -> bool:
        """Validate DNA compliance structure and requirements."""
        required_sections = ["design_principles_validation", "architecture_compliance"]
        
        for section in required_sections:
            if section not in dna_compliance:
                return False
        
        # Validate design principles
        design_principles = dna_compliance["design_principles_validation"]
        required_principles = [
            "pedagogical_value", "policy_to_practice", "time_respect",
            "holistic_thinking", "professional_tone"
        ]
        
        for principle in required_principles:
            if principle not in design_principles:
                return False
        
        # Validate architecture compliance
        architecture = dna_compliance["architecture_compliance"]
        required_architecture = [
            "api_first", "stateless_backend", 
            "separation_of_concerns", "simplicity_first"
        ]
        
        for arch_principle in required_architecture:
            if arch_principle not in architecture:
                return False
        
        return True
    
    def _validate_agent_sequence(self, source_agent: str, target_agent: str) -> bool:
        """Validate that agent handoff sequence is valid."""
        valid_sequences = {
            "project_manager": ["game_designer"],
            "game_designer": ["developer"],
            "developer": ["test_engineer"],
            "test_engineer": ["qa_tester"],
            "qa_tester": ["quality_reviewer"],
            "quality_reviewer": ["project_manager"]  # For next iteration
        }
        
        valid_targets = valid_sequences.get(source_agent, [])
        return target_agent in valid_targets
    
    def _validate_file_paths(self, contract: Dict[str, Any]) -> bool:
        """Validate that file paths follow project conventions."""
        story_id = contract.get("story_id", "")
        
        # Check input files have correct story_id format
        input_files = contract.get("input_requirements", {}).get("required_files", [])
        for file_path in input_files:
            if "{story_id}" in file_path and story_id not in file_path.replace("{story_id}", story_id):
                return False
        
        # Check output files have correct story_id format
        output_files = contract.get("output_specifications", {}).get("deliverable_files", [])
        for file_path in output_files:
            if "{story_id}" in file_path and story_id not in file_path.replace("{story_id}", story_id):
                return False
        
        return True
    
    def _check_quality_gate(self, gate: str, deliverables: Dict[str, Any]) -> bool:
        """Check if specific quality gate passes."""
        # Implementation would check specific quality gates
        # This is a placeholder for the actual quality gate logic
        quality_gate_checkers = {
            "typescript_compilation_success_zero_errors": self._check_typescript_compilation,
            "eslint_standards_compliance_verified": self._check_eslint_compliance,
            "api_response_time_under_200ms_confirmed": self._check_api_performance,
            "100_percent_unit_test_coverage_achieved": self._check_test_coverage,
            "lighthouse_score_above_90_all_categories": self._check_lighthouse_score
        }
        
        checker = quality_gate_checkers.get(gate)
        if checker:
            return checker(deliverables)
        
        # Default to True for undefined gates (should be implemented)
        return True
    
    def _check_typescript_compilation(self, deliverables: Dict[str, Any]) -> bool:
        """Check TypeScript compilation status."""
        # Implementation would run tsc and check for errors
        return True  # Placeholder
    
    def _check_eslint_compliance(self, deliverables: Dict[str, Any]) -> bool:
        """Check ESLint compliance."""
        # Implementation would run ESLint and check for violations
        return True  # Placeholder
    
    def _check_api_performance(self, deliverables: Dict[str, Any]) -> bool:
        """Check API response times."""
        # Implementation would test API endpoints and measure response times
        return True  # Placeholder
    
    def _check_test_coverage(self, deliverables: Dict[str, Any]) -> bool:
        """Check test coverage percentage."""
        # Implementation would run coverage tools and check percentage
        return True  # Placeholder
    
    def _check_lighthouse_score(self, deliverables: Dict[str, Any]) -> bool:
        """Check Lighthouse performance score."""
        # Implementation would run Lighthouse and check scores
        return True  # Placeholder

class DNAValidator:
    """
    Validates decisions and outputs against Project DNA principles.
    
    PURPOSE:
    Ensures all agent decisions align with project DNA, maintaining
    consistency and quality across the entire team.
    """
    
    def __init__(self, dna_docs_path: str = "docs/dna/"):
        self.dna_path = Path(dna_docs_path)
        self.design_principles = self._load_design_principles()
        self.architecture_principles = self._load_architecture_principles()
    
    def _load_design_principles(self) -> Dict[str, Any]:
        """Load design principles from DNA documentation."""
        # Implementation would parse design_principles.md
        return {
            "pedagogical_value": "Every element serves learning objectives",
            "policy_to_practice": "Connect abstract strategy to practical reality",
            "time_respect": "Maximum value in minimal time",
            "holistic_thinking": "Learn systems thinking through action",
            "professional_tone": "Professional tone, never childish"
        }
    
    def _load_architecture_principles(self) -> Dict[str, Any]:
        """Load architecture principles from DNA documentation."""
        # Implementation would parse architecture.md
        return {
            "api_first": "All communication via well-defined REST APIs",
            "stateless_backend": "No server-side state between requests",
            "separation_of_concerns": "Frontend and backend remain separate",
            "simplicity_first": "Choose simplest solution that works"
        }
    
    def validate_decision(self, decision_data: Dict[str, Any], 
                         agent_type: str) -> Dict[str, bool]:
        """
        Validate any agent decision against DNA principles.
        
        Returns dict with validation results for each principle.
        """
        results = {}
        
        # Validate design principles
        results.update(self._validate_design_principles(decision_data, agent_type))
        
        # Validate architecture principles
        results.update(self._validate_architecture_principles(decision_data, agent_type))
        
        return results
    
    def _validate_design_principles(self, decision_data: Dict[str, Any], 
                                  agent_type: str) -> Dict[str, bool]:
        """Validate decision against design principles."""
        # Implementation would check each design principle
        # This is simplified for demonstration
        return {
            "pedagogical_value": True,  # Would check actual pedagogical value
            "policy_to_practice": True,  # Would check practical relevance
            "time_respect": True,  # Would check time constraints
            "holistic_thinking": True,  # Would check systems integration
            "professional_tone": True  # Would check tone and sophistication
        }
    
    def _validate_architecture_principles(self, decision_data: Dict[str, Any], 
                                        agent_type: str) -> Dict[str, bool]:
        """Validate decision against architecture principles."""
        # Implementation would check each architecture principle
        # This is simplified for demonstration
        return {
            "api_first": True,  # Would check API design
            "stateless_backend": True,  # Would check state management
            "separation_of_concerns": True,  # Would check separation
            "simplicity_first": True  # Would check complexity
        }
    
    def require_dna_compliance(self, agent_output: Any) -> bool:
        """
        Block agent output that doesn't meet DNA standards.
        
        Returns True if compliant, raises exception if not.
        """
        validation_results = self.validate_decision(agent_output.__dict__, 
                                                  agent_output.agent_type)
        
        failed_principles = [principle for principle, passed in validation_results.items() 
                           if not passed]
        
        if failed_principles:
            raise DNAComplianceError(
                f"Output violates DNA principles: {failed_principles}"
            )
        
        return True

class DNAComplianceError(Exception):
    """Exception raised when DNA compliance validation fails."""
    pass

class ContractViolationError(Exception):
    """Exception raised when contract validation fails."""
    pass

# Example usage and testing
def test_contract_validation():
    """Test contract validation functionality."""
    
    # Example contract for testing
    test_contract = {
        "contract_version": "1.0",
        "story_id": "STORY-001-001",
        "source_agent": "project_manager",
        "target_agent": "game_designer",
        "dna_compliance": {
            "design_principles_validation": {
                "pedagogical_value": True,
                "policy_to_practice": True,
                "time_respect": True,
                "holistic_thinking": True,
                "professional_tone": True
            },
            "architecture_compliance": {
                "api_first": True,
                "stateless_backend": True,
                "separation_of_concerns": True,
                "simplicity_first": True
            }
        },
        "input_requirements": {
            "required_files": ["docs/stories/story_description_STORY-001-001.md"],
            "required_data": {
                "feature_description": "string",
                "acceptance_criteria": ["string"]
            },
            "required_validations": ["dna_design_principles_alignment_verified"]
        },
        "output_specifications": {
            "deliverable_files": ["docs/specs/game_design_STORY-001-001.md"],
            "deliverable_data": {
                "game_mechanics": "object"
            },
            "validation_criteria": ["all_5_design_principles_addressed_in_game_mechanics"]
        },
        "quality_gates": ["game_mechanics_pedagogical_value_validation"],
        "handoff_criteria": ["game_design_document_completeness"]
    }
    
    validator = ContractValidator()
    
    # Test schema validation
    schema_errors = validator.validate_contract_structure(test_contract)
    print(f"Schema validation errors: {schema_errors}")
    
    # Test business rules validation
    business_errors = validator.validate_contract_business_rules(test_contract)
    print(f"Business rules errors: {business_errors}")
    
    # Test DNA validation
    dna_validator = DNAValidator()
    decision_data = {"feature_type": "learning_game", "complexity": "medium"}
    dna_results = dna_validator.validate_decision(decision_data, "game_designer")
    print(f"DNA validation results: {dna_results}")

if __name__ == "__main__":
    test_contract_validation()
```

---

## 📊 **CONTRACT MONITORING AND METRICS**

### **Contract Performance Tracking**

```python
class ContractMonitor:
    """
    Monitors contract performance and identifies improvement opportunities.
    
    PURPOSE:
    Tracks how well the contract system is working and identifies
    bottlenecks or frequent failure points for optimization.
    """
    
    def __init__(self):
        self.performance_metrics = {}
        self.failure_patterns = {}
    
    def track_contract_execution(self, contract_id: str, 
                               execution_time: float, 
                               success: bool, 
                               failure_reason: Optional[str] = None):
        """Track contract execution metrics."""
        
        if contract_id not in self.performance_metrics:
            self.performance_metrics[contract_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "average_execution_time": 0,
                "failure_count": 0
            }
        
        metrics = self.performance_metrics[contract_id]
        metrics["total_executions"] += 1
        
        if success:
            metrics["successful_executions"] += 1
        else:
            metrics["failure_count"] += 1
            if failure_reason:
                if failure_reason not in self.failure_patterns:
                    self.failure_patterns[failure_reason] = 0
                self.failure_patterns[failure_reason] += 1
        
        # Update average execution time
        current_avg = metrics["average_execution_time"]
        total_count = metrics["total_executions"]
        metrics["average_execution_time"] = (
            (current_avg * (total_count - 1) + execution_time) / total_count
        )
    
    def get_contract_health_report(self) -> Dict[str, Any]:
        """Generate health report for contract system."""
        
        total_contracts = len(self.performance_metrics)
        overall_success_rate = 0
        problematic_contracts = []
        
        for contract_id, metrics in self.performance_metrics.items():
            success_rate = (
                metrics["successful_executions"] / metrics["total_executions"]
                if metrics["total_executions"] > 0 else 0
            )
            
            overall_success_rate += success_rate
            
            if success_rate < 0.9:  # Less than 90% success rate
                problematic_contracts.append({
                    "contract_id": contract_id,
                    "success_rate": success_rate,
                    "avg_execution_time": metrics["average_execution_time"]
                })
        
        overall_success_rate = (
            overall_success_rate / total_contracts 
            if total_contracts > 0 else 0
        )
        
        return {
            "overall_success_rate": overall_success_rate,
            "total_contracts_monitored": total_contracts,
            "problematic_contracts": problematic_contracts,
            "common_failure_patterns": dict(
                sorted(self.failure_patterns.items(), 
                      key=lambda x: x[1], reverse=True)[:5]
            )
        }
```

---

## 🔧 **CONTRACT EVOLUTION AND VERSIONING**

### **Contract Version Management**

```python
class ContractVersionManager:
    """
    Manages contract versions and backward compatibility.
    
    PURPOSE:
    Allows safe evolution of contracts while maintaining compatibility
    with existing agent implementations.
    """
    
    def __init__(self):
        self.version_history = {}
        self.compatibility_matrix = {}
    
    def register_contract_version(self, contract_type: str, 
                                version: str, 
                                schema: Dict[str, Any]):
        """Register a new contract version."""
        
        if contract_type not in self.version_history:
            self.version_history[contract_type] = {}
        
        self.version_history[contract_type][version] = {
            "schema": schema,
            "registration_date": datetime.now(),
            "deprecated": False
        }
    
    def check_compatibility(self, source_agent_version: str, 
                          target_agent_version: str, 
                          contract_type: str) -> bool:
        """Check if agent versions are compatible for contract type."""
        
        compatibility_key = f"{source_agent_version}→{target_agent_version}→{contract_type}"
        return self.compatibility_matrix.get(compatibility_key, True)
    
    def upgrade_contract(self, old_contract: Dict[str, Any], 
                        target_version: str) -> Dict[str, Any]:
        """Upgrade contract to target version with backward compatibility."""
        
        current_version = old_contract.get("contract_version", "1.0")
        
        if current_version == target_version:
            return old_contract
        
        # Apply version-specific transformations
        upgraded_contract = old_contract.copy()
        upgraded_contract["contract_version"] = target_version
        
        # Add new required fields with defaults
        if target_version == "1.1" and current_version == "1.0":
            upgraded_contract = self._upgrade_1_0_to_1_1(upgraded_contract)
        
        return upgraded_contract
    
    def _upgrade_1_0_to_1_1(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Upgrade contract from version 1.0 to 1.1."""
        
        # Example: Add new monitoring fields
        if "monitoring_requirements" not in contract:
            contract["monitoring_requirements"] = {
                "performance_tracking": True,
                "error_reporting": True,
                "success_metrics": ["completion_time", "quality_score"]
            }
        
        return contract
```