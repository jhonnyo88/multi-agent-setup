"""
Exception Handler for DigiNativa AI Team
=======================================

PURPOSE:
Implements the exception handling mechanisms defined in workflow_exception_handling.md.
Provides automated resolution for common issues and escalation paths for complex problems.

ADAPTATION GUIDE:
🔧 To adapt this for your project:
1. Line 45-80: Update RISK_PATTERNS for your domain-specific issues
2. Line 100-150: Modify resolution strategies for your workflows  
3. Line 200-250: Adjust escalation criteria for your team structure
4. Line 300-350: Customize timeout handling for your development velocity

EXCEPTION CATEGORIES:
Handles the 5 defined risks from workflow_exception_handling.md:
1. Tvetydig specifikation (Ambiguous specifications)
2. Issue-Pingis between Utvecklare & QA (Development-QA loops)
3. Utvecklare driver iväg (Developer drift from spec)
4. Kontextförlust (Context loss / AI amnesia)
5. Verktygsfel (Tool failures)
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from workflows.status_handler import StatusHandler

@dataclass
class ExceptionResolution:
    """
    Structured resolution for an exception.
    
    Contains both the automated actions taken and any human escalation needed.
    """
    risk_type: str
    handled: bool
    actions_taken: List[str]
    escalate_to_human: bool
    escalation_reason: Optional[str] = None
    new_tasks: List[Dict[str, Any]] = None
    retry_recommended: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging and communication."""
        return {
            "risk_type": self.risk_type,
            "handled": self.handled,
            "actions_taken": self.actions_taken,
            "escalate_to_human": self.escalate_to_human,
            "escalation_reason": self.escalation_reason,
            "new_tasks": self.new_tasks or [],
            "retry_recommended": self.retry_recommended,
            "timestamp": datetime.now().isoformat()
        }

class ExceptionHandler:
    """
    Central exception handling system for AI team coordination.
    
    DESIGN PHILOSOPHY:
    - Automated resolution for known patterns
    - Clear escalation when automation isn't sufficient
    - Learning from exceptions to improve future handling
    - Detailed logging for debugging and process improvement
    
    INTEGRATION:
    Used by Projektledare when receiving error status codes from agents.
    Implements the specific procedures from workflow_exception_handling.md.
    
    🔧 ADAPTATION: Modify exception patterns and resolutions for your domain
    """
    
    def __init__(self, status_handler: StatusHandler):
        """Initialize with reference to status handler for coordination."""
        self.status_handler = status_handler
        
        # 🔧 ADAPT: Define exception patterns for your domain
        # These patterns help categorize incoming error status codes
        self.risk_patterns = {
            "risk_1_ambiguous_spec": [
                "FEL_SPEC_TVETYDIG_U",
                "FEL_SPEC_TVETYDIG_TU", 
                "FEL_SPEC_OTESTBAR",
                "FEL_SPEC_UPPDRAG_OKLART"
            ],
            "risk_2_qa_dev_loop": [
                "QA_UNDERKÄND_ITERATION_1",
                "QA_UNDERKÄND_ITERATION_2",
                "QA_UNDERKÄND_ITERATION_3"
            ],
            "risk_3_developer_drift": [
                "QA_UNDERKÄND_SPEC_AVVIKELSE"
            ],
            "risk_4_context_loss": [
                "FEL_KONTEXTFEL_U",
                "FEL_KONTEXTFEL_TU",
                "FEL_KONTEXTFEL"
            ],
            "risk_5_tool_failures": [
                "FEL_VERKTYGSFEL_LIGHTHOUSE",
                "FEL_VERKTYGSFEL_ESLINT",
                "FEL_KQ_VERKTYGSFEL_LIGHTHOUSE",
                "FEL_TESTUTVECKLING_VERKTYG",
                "FEL_IMPLEMENTATION_VERKTYG",
                "FEL_QA_MILJÖPROBLEM"
            ]
        }
        
        # Track exception frequency for learning
        self.exception_history = []
    
    async def handle_exception(self, status_code: str, payload: Dict[str, Any], 
                             story_id: Optional[str] = None) -> ExceptionResolution:
        """
        Main exception handling entry point.
        
        Routes status codes to appropriate risk handling based on patterns
        defined in workflow_exception_handling.md.
        
        Args:
            status_code: Error status code from agent
            payload: Structured error data from agent
            story_id: Optional story ID for context
            
        Returns:
            ExceptionResolution with actions taken and escalation info
            
        🔧 ADAPTATION: Add routing for domain-specific error patterns
        """
        try:
            # Log the exception for analysis
            self._log_exception(status_code, payload, story_id)
            
            # Determine risk type from status code
            risk_type = self._identify_risk_type(status_code)
            
            if risk_type == "risk_1_ambiguous_spec":
                return await self._handle_risk_1_ambiguous_spec(status_code, payload, story_id)
            elif risk_type == "risk_2_qa_dev_loop":
                return await self._handle_risk_2_qa_dev_loop(status_code, payload, story_id)
            elif risk_type == "risk_3_developer_drift":
                return await self._handle_risk_3_developer_drift(status_code, payload, story_id)
            elif risk_type == "risk_4_context_loss":
                return await self._handle_risk_4_context_loss(status_code, payload, story_id)
            elif risk_type == "risk_5_tool_failures":
                return await self._handle_risk_5_tool_failures(status_code, payload, story_id)
            else:
                # Unknown exception pattern - escalate to human
                return ExceptionResolution(
                    risk_type="unknown",
                    handled=False,
                    actions_taken=[f"Logged unknown exception: {status_code}"],
                    escalate_to_human=True,
                    escalation_reason=f"Unknown exception pattern: {status_code}"
                )
                
        except Exception as e:
            # Meta-exception: exception handler failed
            print(f"❌ Exception handler failed: {e}")
            return ExceptionResolution(
                risk_type="handler_failure",
                handled=False,
                actions_taken=[f"Exception handler error: {str(e)}"],
                escalate_to_human=True,
                escalation_reason="Exception handler system failure"
            )
    
    def _identify_risk_type(self, status_code: str) -> Optional[str]:
        """Identify which risk category a status code belongs to."""
        for risk_type, patterns in self.risk_patterns.items():
            if status_code in patterns:
                return risk_type
        return None
    
    async def _handle_risk_1_ambiguous_spec(self, status_code: str, payload: Dict[str, Any], 
                                          story_id: Optional[str]) -> ExceptionResolution:
        """
        Handle Risk 1: Tvetydig eller Ofullständig Specifikation
        
        PROCEDURE (from workflow_exception_handling.md):
        1. Log the risk activation
        2. Pause the original task for the reporting agent
        3. Analyze the feedback from the agent
        4. Create new task for Speldesigner to clarify/correct specification
        5. Monitor Speldesigner's work
        6. When complete, restart original agent with updated spec
        
        🔧 ADAPTATION: Modify clarification process for your domain experts
        """
        actions_taken = []
        
        # Log risk activation
        actions_taken.append(f"Risk 1 aktiverad för Story {story_id} - tvetydig specifikation")
        print(f"🔧 Risk 1: Ambiguous specification detected for {story_id}")
        
        # Extract the specific problem from payload
        problem_description = (
            payload.get("otydlighet_beskrivning") or 
            payload.get("error_message") or 
            payload.get("behov_av_förtydligande") or
            "Unspecified specification ambiguity"
        )
        
        # Create task for Speldesigner to clarify specification
        clarification_task = {
            "agent": "speldesigner",
            "task_type": "specification_clarification",
            "story_id": story_id,
            "priority": "high",
            "description": f"Förtydliga/Korrigera specifikation för Story {story_id}",
            "specific_issue": problem_description,
            "context": {
                "original_error": status_code,
                "reporting_agent": payload.get("agent_name", "unknown"),
                "error_details": payload
            },
            "instructions": [
                "Analysera den rapporterade otydligheten",
                "Uppdatera specifikationen för att adressera problemet", 
                "Säkerställ att uppdateringen följer design_principles.md",
                "Returnera LYCKAD_SPEC_UPPDATERAD när klar"
            ]
        }
        
        actions_taken.append("Skapade förtydligande-uppgift för Speldesigner")
        actions_taken.append(f"Problem: {problem_description}")
        
        return ExceptionResolution(
            risk_type="risk_1_ambiguous_spec",
            handled=True,
            actions_taken=actions_taken,
            escalate_to_human=False,
            new_tasks=[clarification_task],
            retry_recommended=True
        )
    
    async def _handle_risk_2_qa_dev_loop(self, status_code: str, payload: Dict[str, Any], 
                                       story_id: Optional[str]) -> ExceptionResolution:
        """
        Handle Risk 2: "Issue-Pingis" mellan Utvecklare & QA-Testare
        
        PROCEDURE (from workflow_exception_handling.md):
        - If iteration < 3: Create new task for Utvecklare with emphasis on different approach
        - If iteration == 3: Activate deadlock-brytare (Projektledare self-analysis)
        
        This is the most critical exception as it can cause infinite loops.
        
        🔧 ADAPTATION: Adjust iteration thresholds and escalation for your team dynamics
        """
        actions_taken = []
        
        # Extract iteration number from status code
        iteration_count = self.status_handler.get_qa_iteration_count(story_id or "")
        
        actions_taken.append(f"Risk 2 aktiverad - QA underkännande iteration {iteration_count}")
        print(f"🔄 Risk 2: QA-Developer loop detected, iteration {iteration_count}")
        
        if iteration_count < 3:
            # Standard retry with emphasis on different approach
            bug_report = payload.get("buggrapport_länk", "No bug report provided")
            reproduction_steps = payload.get("reproduktionssteg", "No reproduction steps")
            
            retry_task = {
                "agent": "utvecklare",
                "task_type": "bug_fix_retry",
                "story_id": story_id,
                "priority": "high",
                "description": f"Korrigera Story {story_id} - iteration {iteration_count}",
                "context": {
                    "previous_attempts": iteration_count - 1,
                    "qa_feedback": payload,
                    "bug_report": bug_report,
                    "reproduction_steps": reproduction_steps
                },
                "instructions": [
                    f"Tidigare försök har misslyckats {iteration_count - 1} gånger",
                    "Försök en SIGNIFIKANT annorlunda lösningsansats",
                    "Analysera QA-feedbacken noggrant innan kodning",
                    "Fokusera på grundorsaken, inte bara symtomen",
                    "Dokumentera varför den nya ansatsen är annorlunda"
                ]
            }
            
            actions_taken.append(f"Skapade retry-uppgift för Utvecklare (försök {iteration_count})")
            actions_taken.append("Betonade behov av annorlunda ansats")
            
            return ExceptionResolution(
                risk_type="risk_2_qa_dev_loop",
                handled=True,
                actions_taken=actions_taken,
                escalate_to_human=False,
                new_tasks=[retry_task],
                retry_recommended=True
            )
            
        else:
            # iteration_count >= 3: Activate deadlock-brytare
            actions_taken.append("Deadlock-brytare aktiverad - Projektledare självanalys")
            print(f"🚨 Risk 2: Deadlock detected at iteration {iteration_count} - escalating")
            
            deadlock_analysis_task = {
                "agent": "projektledare",
                "task_type": "deadlock_analysis", 
                "story_id": story_id,
                "priority": "critical",
                "description": f"Analysera deadlock för Story {story_id}",
                "context": {
                    "iteration_count": iteration_count,
                    "qa_history": self.status_handler.get_story_status_history(story_id or ""),
                    "current_qa_feedback": payload
                },
                "instructions": [
                    "Granska ursprunglig specifikation grundligt",
                    "Analysera all kod och QA-feedback från alla iterationer", 
                    "Identifiera grundorsak till upprepade fel",
                    "Bestäm om problemet är i spec eller implementation",
                    "Formulera NY, avgörande instruktion för lösning",
                    "Om spec är problemet: delegera till Speldesigner",
                    "Om implementation: ge MYCKET specifik vägledning till Utvecklare"
                ]
            }
            
            return ExceptionResolution(
                risk_type="risk_2_qa_dev_loop_deadlock",
                handled=True,
                actions_taken=actions_taken,
                escalate_to_human=False,  # Let Projektledare try self-analysis first
                new_tasks=[deadlock_analysis_task],
                retry_recommended=False
            )
    
    async def _handle_risk_3_developer_drift(self, status_code: str, payload: Dict[str, Any], 
                                           story_id: Optional[str]) -> ExceptionResolution:
        """
        Handle Risk 3: Utvecklaren "Driver iväg" (Drifting from Spec)
        
        PROCEDURE: 
        1. Log the drift
        2. Review QA report for specific spec violations
        3. Create task for Utvecklare with STRICT spec adherence instructions
        
        🔧 ADAPTATION: Customize for your specification enforcement needs
        """
        actions_taken = []
        
        actions_taken.append(f"Risk 3 aktiverad - Utvecklare driver iväg från spec")
        print(f"📋 Risk 3: Developer drift from specification detected")
        
        # Extract specific spec violations from QA feedback
        qa_feedback = payload.get("qa_feedback", {})
        spec_violations = payload.get("spec_violations", [])
        spec_reference = payload.get("spec_referens", "")
        
        correction_task = {
            "agent": "utvecklare",
            "task_type": "spec_compliance_fix",
            "story_id": story_id,
            "priority": "high",
            "description": f"Korrigera specifikationsavvikelser för Story {story_id}",
            "context": {
                "qa_report": qa_feedback,
                "spec_violations": spec_violations,
                "spec_reference": spec_reference
            },
            "instructions": [
                "HÖGSTA PRIORITET: Följ specifikationen EXAKT",
                "Läs igenom specifikationen igen innan kodning",
                "Implementera ENDAST vad som specificeras",
                "Lägg INTE till extra funktionalitet",
                "Dokumentera hur din implementation följer varje acceptanskriterium",
                "Dubbelkolla mot specifikation innan leverans"
            ]
        }
        
        actions_taken.append("Skapade spec-compliance uppgift för Utvecklare")
        actions_taken.append("Betonade strikt specföljning")
        
        return ExceptionResolution(
            risk_type="risk_3_developer_drift",
            handled=True,
            actions_taken=actions_taken,
            escalate_to_human=False,
            new_tasks=[correction_task],
            retry_recommended=True
        )
    
    async def _handle_risk_4_context_loss(self, status_code: str, payload: Dict[str, Any], 
                                        story_id: Optional[str]) -> ExceptionResolution:
        """
        Handle Risk 4: Kontextförlust ("AI Amnesia")
        
        PROCEDURE:
        1. Identify what context was lost/incorrect
        2. Gather correct context from various sources
        3. Recreate task with complete, correct context
        
        🔧 ADAPTATION: Modify context restoration for your information sources
        """
        actions_taken = []
        
        actions_taken.append("Risk 4 aktiverad - Kontextförlust detekterad")
        print(f"🧠 Risk 4: Context loss detected")
        
        # Identify the specific context problem
        context_problem = payload.get("context_problem", "Unspecified context issue")
        missing_context = payload.get("missing_context", [])
        incorrect_context = payload.get("incorrect_context", {})
        
        # Gather correct context (this would integrate with actual file system)
        corrected_context = {
            "story_specification": f"docs/specs/spec-{story_id}.md",
            "dna_documents": {
                "vision_mission": "docs/dna/vision_and_mission.md",
                "target_audience": "docs/dna/target_audience.md", 
                "design_principles": "docs/dna/design_principles.md",
                "architecture": "docs/dna/architecture.md"
            },
            "workflow_guidance": "docs/workflows/story_lifecycle_guide.md",
            "latest_code_version": "main",  # Would be actual git reference
            "related_stories": []  # Would be populated from database
        }
        
        # Create corrected task
        corrected_task = {
            "agent": payload.get("original_agent", "utvecklare"),
            "task_type": "context_corrected_retry",
            "story_id": story_id,
            "priority": "medium",
            "description": f"Återuppta arbete för Story {story_id} med korrigerad kontext",
            "context": corrected_context,
            "context_notes": {
                "context_problem_resolved": context_problem,
                "previously_missing": missing_context,
                "previously_incorrect": incorrect_context
            },
            "instructions": [
                "Verifiera att all nödvändig kontext nu finns tillgänglig",
                "Läs igenom alla refererade dokument",
                "Fortsätt arbetet från där det avbröts",
                "Rapportera om kontextproblem kvarstår"
            ]
        }
        
        actions_taken.append("Samlade korrekt kontext från alla källor")
        actions_taken.append("Skapade korrigerad uppgift med komplett kontext")
        
        return ExceptionResolution(
            risk_type="risk_4_context_loss",
            handled=True,
            actions_taken=actions_taken,
            escalate_to_human=False,
            new_tasks=[corrected_task],
            retry_recommended=True
        )
    
    async def _handle_risk_5_tool_failures(self, status_code: str, payload: Dict[str, Any], 
                                         story_id: Optional[str]) -> ExceptionResolution:
        """
        Handle Risk 5: Verktygsfel hos agenter
        
        PROCEDURE:
        1. Identify which tool failed and why
        2. Attempt automatic retry once
        3. If retry fails, escalate for manual tool debugging
        
        🔧 ADAPTATION: Add tool-specific recovery procedures for your toolchain
        """
        actions_taken = []
        
        failed_tool = payload.get("verktyg", payload.get("tool", "unknown"))
        error_message = payload.get("felmeddelande", payload.get("error_message", ""))
        
        actions_taken.append(f"Risk 5 aktiverad - Verktygsfel: {failed_tool}")
        print(f"🔧 Risk 5: Tool failure detected: {failed_tool}")
        
        # Check if this tool has failed recently (avoid infinite retry loops)
        recent_failures = self._count_recent_tool_failures(failed_tool, hours=1)
        
        if recent_failures < 2:
            # Attempt automatic retry
            retry_task = {
                "agent": payload.get("original_agent", "kvalitetsgranskare"),
                "task_type": "tool_retry",
                "story_id": story_id,
                "priority": "medium",
                "description": f"Försök köra om {failed_tool} för Story {story_id}",
                "context": {
                    "failed_tool": failed_tool,
                    "previous_error": error_message,
                    "retry_attempt": recent_failures + 1
                },
                "instructions": [
                    f"Försök köra {failed_tool} igen",
                    "Kontrollera att verktyget är korrekt konfigurerat",
                    "Om fel kvarstår, rapportera för manuell felsökning",
                    "Dokumentera alla observerade skillnader från föregående försök"
                ]
            }
            
            actions_taken.append(f"Skapade retry-uppgift för {failed_tool}")
            actions_taken.append(f"Detta är försök #{recent_failures + 1}")
            
            return ExceptionResolution(
                risk_type="risk_5_tool_failures",
                handled=True,
                actions_taken=actions_taken,
                escalate_to_human=False,
                new_tasks=[retry_task],
                retry_recommended=True
            )
        else:
            # Too many recent failures - escalate to human
            actions_taken.append(f"För många fel från {failed_tool} senaste timmen")
            actions_taken.append("Eskalerar för manuell verktygsunderhåll")
            
            return ExceptionResolution(
                risk_type="risk_5_tool_failures_persistent",
                handled=False,
                actions_taken=actions_taken,
                escalate_to_human=True,
                escalation_reason=f"Persistent tool failure: {failed_tool} failed {recent_failures + 1} times in 1 hour"
            )
    
    async def handle_timeout(self, story_id: str, agent_name: str, 
                           elapsed_time: timedelta) -> ExceptionResolution:
        """
        Handle story timeouts (when agents don't respond within expected time).
        
        TIMEOUT STRATEGY:
        1. Check if agent is actually stuck or just taking longer than expected
        2. Attempt to restart agent task with additional context
        3. If persistent timeout, escalate to human intervention
        
        🔧 ADAPTATION: Adjust timeout handling for your team's velocity expectations
        """
        actions_taken = []
        
        actions_taken.append(f"Timeout detekterad för {agent_name} på Story {story_id}")
        actions_taken.append(f"Förfluten tid: {elapsed_time}")
        print(f"⏰ Timeout: {agent_name} on {story_id} after {elapsed_time}")
        
        # Check if this agent has had recent timeouts
        recent_timeouts = self._count_recent_timeouts(agent_name, hours=24)
        
        if recent_timeouts < 2:
            # First timeout - try restart with additional guidance
            restart_task = {
                "agent": agent_name,
                "task_type": "timeout_restart",
                "story_id": story_id,
                "priority": "high",
                "description": f"Återstart av {agent_name} för Story {story_id} efter timeout",
                "context": {
                    "timeout_duration": str(elapsed_time),
                    "restart_attempt": recent_timeouts + 1,
                    "additional_guidance": True
                },
                "instructions": [
                    "Börja om från början med denna uppgift",
                    "Fokusera på snabb leverans av grundfunktionalitet",
                    "Rapportera framsteg var 30:e minut",
                    "Be om hjälp om du fastnar på specifika problem",
                    "Prioritera 'good enough' lösning före perfekt lösning"
                ]
            }
            
            actions_taken.append("Skapade restart-uppgift med förstärkt guidning")
            
            return ExceptionResolution(
                risk_type="timeout_restart",
                handled=True,
                actions_taken=actions_taken,
                escalate_to_human=False,
                new_tasks=[restart_task],
                retry_recommended=True
            )
        else:
            # Multiple timeouts - escalate to human
            actions_taken.append(f"Flera timeouts för {agent_name} senaste 24h")
            actions_taken.append("Möjlig systemproblem eller agent-konfigurationsfel")
            
            return ExceptionResolution(
                risk_type="persistent_timeout",
                handled=False,
                actions_taken=actions_taken,
                escalate_to_human=True,
                escalation_reason=f"Agent {agent_name} has timed out {recent_timeouts + 1} times in 24 hours"
            )
    
    def _log_exception(self, status_code: str, payload: Dict[str, Any], story_id: Optional[str]):
        """Log exception for analysis and improvement."""
        exception_record = {
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code,
            "story_id": story_id,
            "payload": payload,
            "risk_type": self._identify_risk_type(status_code)
        }
        
        self.exception_history.append(exception_record)
        
        # Keep only recent exceptions to prevent memory growth
        if len(self.exception_history) > 1000:
            self.exception_history = self.exception_history[-500:]
    
    def _count_recent_tool_failures(self, tool_name: str, hours: int = 1) -> int:
        """Count recent failures for a specific tool."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        count = 0
        for record in self.exception_history:
            record_time = datetime.fromisoformat(record["timestamp"])
            if (record_time > cutoff_time and 
                record["payload"].get("verktyg") == tool_name):
                count += 1
        
        return count
    
    def _count_recent_timeouts(self, agent_name: str, hours: int = 24) -> int:
        """Count recent timeouts for a specific agent."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        count = 0
        for record in self.exception_history:
            record_time = datetime.fromisoformat(record["timestamp"])
            if (record_time > cutoff_time and 
                "timeout" in record["status_code"].lower()):
                count += 1
        
        return count
    
    def get_exception_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get exception statistics for monitoring and improvement.
        
        Useful for identifying patterns and improving agent performance.
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        recent_exceptions = [
            record for record in self.exception_history
            if datetime.fromisoformat(record["timestamp"]) > cutoff_time
        ]
        
        stats = {
            "total_exceptions": len(recent_exceptions),
            "exceptions_by_risk": {},
            "exceptions_by_agent": {},
            "most_common_errors": {},
            "resolution_rate": 0.0
        }
        
        # Categorize exceptions
        for record in recent_exceptions:
            risk_type = record.get("risk_type", "unknown")
            stats["exceptions_by_risk"][risk_type] = stats["exceptions_by_risk"].get(risk_type, 0) + 1
            
            status_code = record["status_code"]
            stats["most_common_errors"][status_code] = stats["most_common_errors"].get(status_code, 0) + 1
        
        return stats

# Convenience functions for Projektledare
async def handle_agent_exception(status_code: str, payload: Dict[str, Any], 
                                story_id: Optional[str] = None) -> ExceptionResolution:
    """Convenience function for handling exceptions."""
    status_handler = StatusHandler()
    exception_handler = ExceptionHandler(status_handler)
    return await exception_handler.handle_exception(status_code, payload, story_id)