
"""
PROJEKTLEDARE OUTPUT CONTRACTS
=============================

THIS FILE DEFINES THE IMMUTABLE INTERFACE
Changes here break the entire system - only additive changes allowed

PURPOSE: Define all output data structures for Projektledare agent
GUARANTEE: These contracts can ONLY be extended with optional fields
RULE: Existing fields can NEVER be changed or removed

VERSION: 1.0.0
BACKWARD_COMPATIBILITY: Must maintain forever
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum

class AnalysisStatus(Enum):
    """Analysis result status"""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CLARIFICATION = "needs_clarification"
    DEFERRED = "deferred"

class StoryStatus(Enum):
    """Story creation status"""
    CREATED = "created"
    FAILED = "failed"
    PARTIAL = "partial"

class CoordinationStatus(Enum):
    """Team coordination status"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"

class FeatureAnalysis(BaseModel):
    """Detailed feature analysis results"""
    recommendation: str = Field(..., description="Overall recommendation (approve/reject/clarify)")
    feasibility_score: float = Field(..., description="Technical feasibility (0.0-1.0)")
    complexity_estimate: int = Field(..., description="Complexity rating (1-10)")
    estimated_effort_hours: int = Field(..., description="Estimated development hours")
    
    # Analysis details
    technical_assessment: Dict[str, Any] = Field(..., description="Technical analysis details")
    business_value: Optional[str] = Field(default=None, description="Business value assessment")
    risks: List[str] = Field(default=[], description="Identified risks")
    dependencies: List[str] = Field(default=[], description="Technical dependencies")
    
    # DNA alignment
    design_principles_alignment: Dict[str, bool] = Field(..., description="Alignment with design principles")
    target_audience_fit: bool = Field(..., description="Fits target audience needs")
    
    # Implementation guidance
    suggested_approach: Optional[str] = Field(default=None, description="Recommended implementation approach")
    quality_requirements: List[str] = Field(default=[], description="Specific quality requirements")

class Story(BaseModel):
    """Individual story definition"""
    story_id: str = Field(..., description="Unique story identifier")
    title: str = Field(..., description="Story title")
    description: str = Field(..., description="Detailed story description")
    
    # Assignment
    assigned_agent: str = Field(..., description="Agent type assigned to story")
    story_type: str = Field(..., description="Type of story (spec, implementation, testing, etc.)")
    
    # Requirements
    acceptance_criteria: List[str] = Field(..., description="Acceptance criteria for story completion")
    dependencies: List[str] = Field(default=[], description="Other stories this depends on")
    
    # Estimation
    complexity: int = Field(..., description="Story complexity (1-5)")
    estimated_hours: int = Field(..., description="Estimated effort in hours")
    
    # GitHub integration
    github_issue_id: Optional[int] = Field(default=None, description="Created GitHub issue ID")
    github_url: Optional[str] = Field(default=None, description="GitHub issue URL")

class FeatureAnalysisResponse(BaseModel):
    """
    IMMUTABLE OUTPUT CONTRACT for Projektledare feature analysis
    
    This contract can ONLY be extended with optional fields.
    Existing fields can NEVER be changed or removed.
    """
    # Core response (REQUIRED - never change)
    request_id: str = Field(..., description="Request identifier from input")
    status: AnalysisStatus = Field(..., description="Analysis result status")
    
    # Analysis results (REQUIRED - never change)
    analysis: FeatureAnalysis = Field(..., description="Detailed analysis results")
    recommendation_summary: str = Field(..., description="Human-readable recommendation summary")
    
    # Processing details (REQUIRED - never change)
    analysis_time_seconds: float = Field(..., description="Time spent on analysis")
    ai_model_used: str = Field(..., description="AI model used for analysis")
    
    # Next steps (OPTIONAL - can be extended)
    next_actions: Optional[List[str]] = Field(default=[], description="Recommended next actions")
    clarification_questions: Optional[List[str]] = Field(default=[], description="Questions for clarification")
    
    # GitHub integration (OPTIONAL - can be extended)
    github_comment_posted: Optional[bool] = Field(default=False, description="Whether comment was posted to GitHub")
    github_labels_added: Optional[List[str]] = Field(default=[], description="Labels added to GitHub issue")
    
    # Metadata (OPTIONAL - can be extended)
    completed_at: datetime = Field(default_factory=datetime.now)
    agent_version: Optional[str] = Field(default="1.0.0", description="Agent version used")
    
    # Error handling (OPTIONAL - can be extended)
    warnings: Optional[List[str]] = Field(default=[], description="Any warnings encountered")
    errors: Optional[List[str]] = Field(default=[], description="Any errors encountered")
    
    # Future extensibility (SAFE to add new optional fields here)
    # stakeholder_impact: Optional[Dict[str, str]] = Field(default={}, description="Impact on stakeholders")
    # resource_requirements: Optional[Dict[str, Any]] = Field(default={}, description="Required resources")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StoryCreationResponse(BaseModel):
    """
    IMMUTABLE OUTPUT CONTRACT for Projektledare story creation
    """
    # Core response (REQUIRED - never change)
    feature_id: str = Field(..., description="Feature identifier from input")
    status: StoryStatus = Field(..., description="Story creation status")
    
    # Created stories (REQUIRED - never change)
    stories: List[Story] = Field(..., description="All created stories")
    total_stories_created: int = Field(..., description="Number of stories successfully created")
    
    # Execution details (REQUIRED - never change)
    creation_time_seconds: float = Field(..., description="Time spent creating stories")
    github_issues_created: int = Field(..., description="Number of GitHub issues created")
    
    # Agent assignments (OPTIONAL - can be extended)
    agent_assignments: Optional[Dict[str, List[str]]] = Field(default={}, description="Stories assigned to each agent")
    execution_order: Optional[List[str]] = Field(default=[], description="Recommended execution order")
    
    # Timeline and planning (OPTIONAL - can be extended)
    estimated_total_effort: Optional[int] = Field(default=None, description="Total estimated effort in hours")
    critical_path: Optional[List[str]] = Field(default=[], description="Critical path story IDs")
    
    # GitHub integration (OPTIONAL - can be extended)
    parent_issue_updated: Optional[bool] = Field(default=False, description="Whether parent issue was updated")
    github_project_board_updated: Optional[bool] = Field(default=False, description="Whether project board was updated")
    
    # Metadata (OPTIONAL - can be extended)
    completed_at: datetime = Field(default_factory=datetime.now)
    created_by_agent: Optional[str] = Field(default="projektledare", description="Agent that created stories")
    
    # Error handling (OPTIONAL - can be extended)
    failed_stories: Optional[List[Dict[str, str]]] = Field(default=[], description="Stories that failed to create")
    warnings: Optional[List[str]] = Field(default=[], description="Any warnings encountered")

class AgentTaskResult(BaseModel):
    """Result from coordinating with individual agent"""
    agent_type: str = Field(..., description="Type of agent")
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Task execution status")
    result: Dict[str, Any] = Field(..., description="Task result data")
    execution_time_seconds: float = Field(..., description="Task execution time")
    
    # Error details if failed
    error_message: Optional[str] = Field(default=None, description="Error message if task failed")
    retry_count: Optional[int] = Field(default=0, description="Number of retries attempted")

class TeamCoordinationResponse(BaseModel):
    """
    IMMUTABLE OUTPUT CONTRACT for Projektledare team coordination
    """
    # Core response (REQUIRED - never change)
    coordination_type: str = Field(..., description="Coordination type from input")
    status: CoordinationStatus = Field(..., description="Overall coordination status")
    
    # Agent results (REQUIRED - never change)
    agent_results: List[AgentTaskResult] = Field(..., description="Results from each coordinated agent")
    successful_agents: int = Field(..., description="Number of agents that completed successfully")
    failed_agents: int = Field(..., description="Number of agents that failed")
    
    # Execution details (REQUIRED - never change)
    coordination_time_seconds: float = Field(..., description="Total coordination time")
    total_agents_coordinated: int = Field(..., description="Total number of agents involved")
    
    # Workflow state (OPTIONAL - can be extended)
    workflow_state_updated: Optional[bool] = Field(default=False, description="Whether workflow state was updated")
    next_coordination_needed: Optional[bool] = Field(default=False, description="Whether additional coordination is needed")
    
    # Error handling and recovery (OPTIONAL - can be extended)
    recovery_actions_taken: Optional[List[str]] = Field(default=[], description="Recovery actions performed")
    failed_agent_details: Optional[List[Dict[str, Any]]] = Field(default=[], description="Details of failed agents")
    
    # Metadata (OPTIONAL - can be extended)
    completed_at: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracking")
    
    # Future extensibility (SAFE to add new optional fields here)
    # performance_metrics: Optional[Dict[str, float]] = Field(default={}, description="Performance metrics")
    # resource_utilization: Optional[Dict[str, Any]] = Field(default={}, description="Resource usage statistics")

# Union type for all possible outputs from Projektledare
ProjektledareOutput = Union[FeatureAnalysisResponse, StoryCreationResponse, TeamCoordinationResponse]