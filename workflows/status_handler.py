"""
Status Handler for DigiNativa AI Team
====================================

PURPOSE:
Centralized status management for all AI agents. Handles status codes,
structured feedback, and communication between agents via the Projektledare.

ADAPTATION GUIDE:
🔧 To adapt this for your project:
1. Line 45-60: Update STATUS_CODES for your domain workflows
2. Line 80-100: Modify validation rules for your agent types
3. Line 120-140: Adjust status persistence for your infrastructure
4. Line 200-220: Customize status analysis for your success metrics

CORE FUNCTIONALITY:
- Validates and stores agent status reports with structured JSON payloads
- Provides status querying and filtering for workflow coordination
- Handles status code interpretation for exception handling
- Maintains audit trail of all agent communications
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from config.settings import STATE_DIR, PROJECT_DOMAIN

@dataclass
class StatusReport:
    """
    Structured status report from an AI agent.
    
    This is the core communication format between agents and the Projektledare.
    Every agent interaction results in a StatusReport with standardized structure.
    """
    agent_name: str
    status_code: str
    timestamp: datetime
    payload: Dict[str, Any]
    story_id: Optional[str] = None
    correlation_id: Optional[str] = None  # For tracking related operations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusReport':
        """Create from dictionary (e.g., from database)."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class StatusHandler:
    """
    Central handler for all agent status communications.
    
    DESIGN PRINCIPLES:
    - All agent communication goes through structured status codes
    - Persistent storage enables recovery and auditing
    - Standardized format enables automated workflow decisions
    - Exception handling based on status code patterns
    
    🔧 ADAPTATION: Modify status codes and validation for your domain
    """
    
    def __init__(self):
        """Initialize status handler with database connection."""
        self.db_path = STATE_DIR / "agent_status.db"
        self._init_database()
        
        # 🔧 ADAPT: Define status codes for your domain and workflows
        # These codes guide Projektledare's decision-making
        self.SUCCESS_CODES = {
            # Speldesigner success codes
            "LYCKAD_SPEC_LEVERERAD",
            "LYCKAD_SPEC_UPPDATERAD", 
            
            # Utvecklare success codes
            "LYCKAD_KOD_IMPLEMENTERAD",
            "LYCKAD_KOD_LEVERERAD",
            
            # Testutvecklare success codes  
            "LYCKAD_TESTER_SKRIVNA",
            "LYCKAD_AUTOMATISK_GRIND_GRÖN",
            
            # QA-Testare success codes
            "QA_GODKÄND",
            "LYCKAD_QA_GODKÄND",
            
            # Kvalitetsgranskare success codes
            "TEKNISK_GRANSKNING_OK",
            
            # Projektledare workflow codes
            "FEATURE_ANALYZED",
            "STORIES_CREATED",
            "STORY_DELEGATED",
            "STORY_COMPLETED"
        }
        
        self.ERROR_CODES = {
            # Specification errors
            "FEL_SPEC_UPPDRAG_OKLART",
            "FEL_SPEC_TVETYDIG_U",
            "FEL_SPEC_TVETYDIG_TU", 
            "FEL_SPEC_OTESTBAR",
            
            # Implementation errors
            "FEL_IMPLEMENTATION_ARKITEKTURBROTT",
            "FEL_IMPLEMENTATION_VERKTYG",
            "FEL_KOD_EJ_TESTBAR",
            
            # Context and communication errors
            "FEL_KONTEXTFEL_U",
            "FEL_KONTEXTFEL_TU",
            "FEL_KONTEXTFEL",
            
            # Quality gate failures
            "FEL_REGRESSIONSTEST",
            "FEL_KVALITETSGRIND_PRESTANDA",
            "FEL_KVALITETSGRIND_KODSTANDARD",
            "FEL_KVALITETSGRIND_TILLGÄNGLIGHET",
            
            # Tool and infrastructure errors
            "FEL_VERKTYGSFEL_LIGHTHOUSE",
            "FEL_VERKTYGSFEL_ESLINT", 
            "FEL_KQ_KODBAS_OTILLGÄNGLIG",
            "FEL_KQ_VERKTYGSFEL_LIGHTHOUSE",
            "FEL_QA_MILJÖPROBLEM",
            "FEL_TESTUTVECKLING_VERKTYG",
            
            # Projektledare errors
            "ANALYSIS_ERROR",
            "DELEGATION_FAILED",
            "STORY_TIMEOUT"
        }
        
        self.QA_ITERATION_CODES = {
            # QA failure codes with iteration tracking (for deadlock detection)
            "QA_UNDERKÄND_ITERATION_1",
            "QA_UNDERKÄND_ITERATION_2", 
            "QA_UNDERKÄND_ITERATION_3",  # Triggers deadlock handling
            "QA_UNDERKÄND_SPEC_AVVIKELSE"
        }
        
        # 🔧 ADAPT: Add domain-specific status codes here
        # Examples for other domains:
        # E-commerce: "PAYMENT_INTEGRATION_SUCCESS", "CART_VALIDATION_FAILED"
        # Mobile app: "UI_RESPONSIVE_VALIDATED", "PERFORMANCE_BENCHMARK_FAILED"
        # SaaS: "API_INTEGRATION_TESTED", "MULTI_TENANT_ISOLATED"
    
    def _init_database(self):
        """
        Initialize SQLite database for status storage.
        
        SCHEMA DESIGN:
        - status_reports: Main table for all agent communications
        - Indexes on agent_name, status_code, story_id for fast queries
        - JSON payload storage for flexible structured data
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS status_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    status_code TEXT NOT NULL, 
                    timestamp TEXT NOT NULL,
                    story_id TEXT,
                    correlation_id TEXT,
                    payload TEXT NOT NULL,  -- JSON string
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for fast queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_name 
                ON status_reports(agent_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_code 
                ON status_reports(status_code)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_story_id 
                ON status_reports(story_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON status_reports(timestamp)
            """)
            
            conn.commit()
    
    def report_status(self, agent_name: str, status_code: str, 
                     payload: Dict[str, Any], story_id: Optional[str] = None,
                     correlation_id: Optional[str] = None) -> bool:
        """
        Report a status from an AI agent.
        
        This is the primary method agents use to communicate with the Projektledare.
        All agent outcomes (success, failure, requests for help) go through this method.
        
        Args:
            agent_name: Name of the reporting agent (e.g., "speldesigner", "utvecklare")
            status_code: Standardized status code indicating outcome
            payload: Structured data with details about the status
            story_id: Optional story ID if this relates to a specific story
            correlation_id: Optional ID for tracking related operations
            
        Returns:
            True if status was successfully recorded, False otherwise
            
        🔧 ADAPTATION: Add validation rules specific to your domain
        """
        try:
            # Validate inputs
            if not self._validate_status_report(agent_name, status_code, payload):
                print(f"❌ Invalid status report from {agent_name}: {status_code}")
                return False
            
            # Create status report
            report = StatusReport(
                agent_name=agent_name,
                status_code=status_code,
                timestamp=datetime.now(),
                payload=payload,
                story_id=story_id,
                correlation_id=correlation_id
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO status_reports 
                    (agent_name, status_code, timestamp, story_id, correlation_id, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    report.agent_name,
                    report.status_code, 
                    report.timestamp.isoformat(),
                    report.story_id,
                    report.correlation_id,
                    json.dumps(report.payload, ensure_ascii=False)
                ))
                conn.commit()
            
            # Log for debugging
            print(f"✅ Status recorded: {agent_name} -> {status_code}")
            if story_id:
                print(f"   Story: {story_id}")
            if payload:
                print(f"   Payload keys: {list(payload.keys())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to record status from {agent_name}: {e}")
            return False
    
    def _validate_status_report(self, agent_name: str, status_code: str, 
                               payload: Dict[str, Any]) -> bool:
        """
        Validate status report before storing.
        
        VALIDATION RULES:
        - Agent name must be recognized
        - Status code must be in defined sets
        - Payload must contain required fields for the status code
        - Error status codes must include error descriptions
        
        🔧 ADAPTATION: Add validation rules for your agents and status codes
        """
        # Validate agent name
        valid_agents = {
            "projektledare", "speldesigner", "utvecklare", 
            "testutvecklare", "qa_testare", "kvalitetsgranskare"
        }
        # 🔧 ADAPT: Update with your agent names
        
        if agent_name not in valid_agents:
            print(f"❌ Unknown agent name: {agent_name}")
            return False
        
        # Validate status code format
        all_valid_codes = self.SUCCESS_CODES | self.ERROR_CODES | self.QA_ITERATION_CODES
        if status_code not in all_valid_codes:
            print(f"❌ Unknown status code: {status_code}")
            return False
        
        # Validate payload structure based on status code
        if self.is_error_status(status_code):
            # Error statuses must include error description
            if "error" not in payload and "error_message" not in payload:
                print(f"❌ Error status {status_code} missing error description")
                return False
        
        # Validate QA iteration codes have iteration tracking
        if status_code in self.QA_ITERATION_CODES:
            if "iteration" not in payload and "_ITERATION_" not in status_code:
                print(f"❌ QA iteration status missing iteration info")
                return False
        
        return True
    
    def get_latest_status(self, agent_name: str, story_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the most recent status from a specific agent.
        
        Used by Projektledare to check current state of agent work.
        
        Args:
            agent_name: Name of agent to query
            story_id: Optional filter by specific story
            
        Returns:
            Most recent status report as dictionary, or None if no status found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if story_id:
                    cursor = conn.execute("""
                        SELECT agent_name, status_code, timestamp, story_id, correlation_id, payload
                        FROM status_reports 
                        WHERE agent_name = ? AND story_id = ?
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    """, (agent_name, story_id))
                else:
                    cursor = conn.execute("""
                        SELECT agent_name, status_code, timestamp, story_id, correlation_id, payload
                        FROM status_reports 
                        WHERE agent_name = ?
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    """, (agent_name,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "agent_name": row[0],
                        "status_code": row[1],
                        "timestamp": row[2], 
                        "story_id": row[3],
                        "correlation_id": row[4],
                        "payload": json.loads(row[5])
                    }
                return None
                
        except Exception as e:
            print(f"❌ Failed to get latest status for {agent_name}: {e}")
            return None
    
    def get_story_status_history(self, story_id: str) -> List[Dict[str, Any]]:
        """
        Get complete status history for a specific story.
        
        Used by Projektledare to understand story progression and debug issues.
        
        Args:
            story_id: Story ID to query
            
        Returns:
            List of status reports chronologically ordered
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT agent_name, status_code, timestamp, story_id, correlation_id, payload
                    FROM status_reports 
                    WHERE story_id = ?
                    ORDER BY timestamp ASC
                """, (story_id,))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        "agent_name": row[0],
                        "status_code": row[1],
                        "timestamp": row[2],
                        "story_id": row[3], 
                        "correlation_id": row[4],
                        "payload": json.loads(row[5])
                    })
                
                return history
                
        except Exception as e:
            print(f"❌ Failed to get story history for {story_id}: {e}")
            return []
    
    def is_success_status(self, status_code: str) -> bool:
        """Check if status code indicates successful completion."""
        return status_code in self.SUCCESS_CODES
    
    def is_error_status(self, status_code: str) -> bool:
        """Check if status code indicates an error condition."""
        return status_code in self.ERROR_CODES
    
    def is_qa_iteration_status(self, status_code: str) -> bool:
        """Check if status code is a QA iteration (for deadlock detection)."""
        return status_code in self.QA_ITERATION_CODES
    
    def get_qa_iteration_count(self, story_id: str) -> int:
        """
        Get the current QA iteration count for deadlock detection.
        
        This helps Projektledare determine when to activate deadlock handling
        (Risk 2 in workflow_exception_handling.md).
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT status_code FROM status_reports
                    WHERE story_id = ? AND status_code LIKE 'QA_UNDERKÄND_ITERATION_%'
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (story_id,))
                
                row = cursor.fetchone()
                if row:
                    # Extract iteration number from status code
                    status_code = row[0]
                    if "_ITERATION_" in status_code:
                        iteration_str = status_code.split("_ITERATION_")[-1]
                        try:
                            return int(iteration_str)
                        except ValueError:
                            return 0
                return 0
                
        except Exception as e:
            print(f"❌ Failed to get QA iteration count for {story_id}: {e}")
            return 0
    
    def cleanup_old_statuses(self, days_to_keep: int = 30):
        """
        Clean up old status reports to prevent database growth.
        
        Keeps recent statuses for active debugging but removes old data.
        Should be run periodically via scheduled task.
        
        🔧 ADAPTATION: Adjust retention period based on your audit requirements
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM status_reports 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"🧹 Cleaned up {deleted_count} old status reports (older than {days_to_keep} days)")
                
        except Exception as e:
            print(f"❌ Failed to cleanup old statuses: {e}")

# Convenience functions for agents to use
def report_success(agent_name: str, status_code: str, **kwargs):
    """Convenience function for agents to report success."""
    handler = StatusHandler()
    return handler.report_status(agent_name, status_code, kwargs)

def report_error(agent_name: str, status_code: str, error_message: str, **kwargs):
    """Convenience function for agents to report errors."""
    handler = StatusHandler()
    payload = {"error_message": error_message, **kwargs}
    return handler.report_status(agent_name, status_code, payload)

def get_agent_status(agent_name: str, story_id: Optional[str] = None):
    """Convenience function to get agent status."""
    handler = StatusHandler()
    return handler.get_latest_status(agent_name, story_id)