"""
Priority Queue Manager för DigiNativa AI-Team
=============================================

PURPOSE:
Manages priority ordering of GitHub Issues according to P0-P3 system.
Ensures AI team always works on highest priority items with clear dependencies.

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Line 45-55: Change priority labels (P0-P3 → your labels)
2. Line 80-100: Modify dependency extraction patterns for your workflow
3. Line 130-150: Update status management for your process

CONFIGURATION POINTS:
- Line 45: Priority labels mapping
- Line 82: Dependency extraction patterns
- Line 165: Issue status determination logic
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import asyncio
from datetime import datetime

class Priority(Enum):
    """Priority levels for GitHub Issues"""
    P0_CRITICAL = 0    # Security fixes, system-critical issues
    P1_HIGH = 1        # Core functionality, user registration
    P2_MEDIUM = 2      # Improvements, optimizations
    P3_LOW = 3         # Nice-to-have features
    UNASSIGNED = 99    # No priority assigned

@dataclass
class PriorityIssue:
    """
    GitHub Issue with priority and dependency information.
    
    Represents a single issue in the priority queue with all metadata
    needed for scheduling and dependency management.
    """
    number: int
    title: str
    priority: Priority
    labels: List[str]
    dependencies: List[int]  # Issue numbers this depends on
    status: str             # open, in_progress, completed, blocked
    body: str
    assigned_agent: Optional[str] = None
    story_breakdown: Optional[List[int]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PriorityQueueManager:
    """
    Manages priority ordering and dependency handling of GitHub Issues.
    
    CORE LOGIC:
    1. Read all open Issues from GitHub
    2. Extract priority from labels (P0, P1, P2, P3)
    3. Identify dependencies from issue body/comments
    4. Return next issue that can be started (highest priority + no blocking dependencies)
    
    EXAMPLE USAGE:
    ```python
    pq = PriorityQueueManager(github_client)
    await pq.refresh_queue()
    next_issue = pq.get_next_available_issue()
    if next_issue:
        print(f"Starting work on: {next_issue.title}")
    ```
    """
    
    def __init__(self, github_client):
        self.github = github_client
        self.current_queue: List[PriorityIssue] = []
        self.completed_issues: set = set()  # Track completed issue numbers
        
    def extract_priority_from_labels(self, labels: List[str]) -> Priority:
        """
        Extract priority from GitHub labels.
        
        PRIORITY MAPPING:
        - P0/Critical → P0_CRITICAL (immediate action)
        - P1/High → P1_HIGH (important features)
        - P2/Medium → P2_MEDIUM (improvements)
        - P3/Low → P3_LOW (nice-to-have)
        
        Args:
            labels: List of label names from GitHub issue
            
        Returns:
            Priority enum value
        """
        for label in labels:
            label_name = label.lower().strip()
            
            # P0 - Critical priority
            if any(keyword in label_name for keyword in ['p0', 'critical', 'urgent', 'security']):
                return Priority.P0_CRITICAL
            
            # P1 - High priority  
            elif any(keyword in label_name for keyword in ['p1', 'high', 'important']):
                return Priority.P1_HIGH
            
            # P2 - Medium priority
            elif any(keyword in label_name for keyword in ['p2', 'medium', 'enhancement']):
                return Priority.P2_MEDIUM
            
            # P3 - Low priority
            elif any(keyword in label_name for keyword in ['p3', 'low', 'nice-to-have']):
                return Priority.P3_LOW
        
        return Priority.UNASSIGNED
    
    def extract_dependencies(self, issue_body: str) -> List[int]:
        """
        Extract dependencies from issue body text.
        
        SUPPORTED PATTERNS:
        - "Depends on #123"
        - "Blocked by #123, #124"
        - "Dependencies: #123"
        - "Requires #123 to be completed first"
        - "Must complete #123 and #124 before starting"
        
        Args:
            issue_body: The issue description text
            
        Returns:
            List of issue numbers this issue depends on
        """
        if not issue_body:
            return []
        
        # Dependency extraction patterns (case insensitive)
        dependency_patterns = [
            r'depends?\s+on[:\s]+[#\s]*(\d+(?:\s*,\s*#?\s*\d+)*)',
            r'blocked\s+by[:\s]+[#\s]*(\d+(?:\s*,\s*#?\s*\d+)*)',
            r'dependencies?[:\s]+[#\s]*(\d+(?:\s*,\s*#?\s*\d+)*)',
            r'requires?[:\s]+[#\s]*(\d+(?:\s*,\s*#?\s*\d+)*)',
            r'must\s+complete[:\s]+[#\s]*(\d+(?:\s*,\s*#?\s*\d+)*)',
            r'needs?[:\s]+[#\s]*(\d+(?:\s*,\s*#?\s*\d+)*)'
        ]
        
        dependencies = []
        
        for pattern in dependency_patterns:
            matches = re.findall(pattern, issue_body, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Extract all numbers from the match string
                numbers = re.findall(r'\d+', match)
                dependencies.extend([int(num) for num in numbers])
        
        # Remove duplicates and return
        return list(set(dependencies))
    
    def determine_issue_status(self, issue_data: Dict, labels: List[str]) -> str:
        """
        Determine current status of an issue from labels and state.
        
        STATUS MAPPING:
        - Labels: "in-progress", "ai-working" → in_progress
        - Labels: "completed", "done" → completed  
        - Labels: "blocked" → blocked
        - Default: open
        
        Args:
            issue_data: GitHub issue data
            labels: List of label names
            
        Returns:
            Status string
        """
        # Check GitHub issue state first
        if issue_data.get('state') == 'closed':
            return 'completed'
        
        # Check labels for status indicators
        label_names = [label.lower().strip() for label in labels]
        
        if any(label in label_names for label in ['in-progress', 'ai-working', 'developing']):
            return 'in_progress'
        elif any(label in label_names for label in ['completed', 'done', 'finished']):
            return 'completed'
        elif any(label in label_names for label in ['blocked', 'waiting', 'on-hold']):
            return 'blocked'
        else:
            return 'open'
    
    async def refresh_queue(self) -> List[PriorityIssue]:
        """
        Update priority queue from GitHub issues.
        
        PROCESS:
        1. Fetch all open issues from GitHub
        2. Extract metadata (priority, dependencies, status)
        3. Create PriorityIssue objects
        4. Sort by priority (P0 first)
        5. Update internal queue
        
        Returns:
            Updated list of priority issues
        """
        try:
            # Fetch issues from GitHub
            issues_data = await self.github.get_open_issues()
            
            priority_issues = []
            
            for issue_data in issues_data:
                # Extract label names
                label_objects = issue_data.get('labels', [])
                label_names = [label.get('name', '') for label in label_objects if isinstance(label, dict)]
                
                # Extract metadata
                priority = self.extract_priority_from_labels(label_names)
                dependencies = self.extract_dependencies(issue_data.get('body', ''))
                status = self.determine_issue_status(issue_data, label_names)
                
                # Create PriorityIssue object
                priority_issue = PriorityIssue(
                    number=issue_data['number'],
                    title=issue_data.get('title', 'Untitled'),
                    priority=priority,
                    labels=label_names,
                    dependencies=dependencies,
                    status=status,
                    body=issue_data.get('body', ''),
                    created_at=issue_data.get('created_at'),
                    updated_at=issue_data.get('updated_at')
                )
                
                priority_issues.append(priority_issue)
            
            # Sort by priority (P0 first, then P1, P2, P3)
            # Secondary sort by creation date (older first)
            self.current_queue = sorted(
                priority_issues, 
                key=lambda x: (
                    x.priority.value,  # Primary sort: priority
                    x.created_at or datetime.min  # Secondary sort: creation date
                )
            )
            
            print(f"✅ Priority queue refreshed: {len(self.current_queue)} issues loaded")
            return self.current_queue
            
        except Exception as e:
            print(f"❌ Error refreshing priority queue: {e}")
            return []
    
    def get_next_available_issue(self) -> Optional[PriorityIssue]:
        """
        Return next issue that can be started.
        
        SELECTION LOGIC:
        1. Sort by priority (P0 → P1 → P2 → P3)
        2. For each issue, check if all dependencies are completed
        3. Return first issue without blocking dependencies
        4. Skip issues already in progress or completed
        
        Returns:
            Next available PriorityIssue or None if no issues available
        """
        # Update completed issues set from current queue
        self.completed_issues.update(
            issue.number for issue in self.current_queue 
            if issue.status == 'completed'
        )
        
        for issue in self.current_queue:
            # Skip if not open status
            if issue.status != 'open':
                continue
            
            # Check if all dependencies are completed
            blocking_deps = [
                dep for dep in issue.dependencies 
                if dep not in self.completed_issues
            ]
            
            if not blocking_deps:
                print(f"🎯 Next available issue: #{issue.number} - {issue.title}")
                print(f"   Priority: {issue.priority.name}")
                if issue.dependencies:
                    print(f"   Dependencies satisfied: {issue.dependencies}")
                return issue
            else:
                print(f"⏸️ Issue #{issue.number} blocked by: {blocking_deps}")
        
        print("📭 No available issues found")
        return None
    
    def mark_issue_in_progress(self, issue_number: int, agent_name: str) -> bool:
        """
        Mark issue as in progress by specific agent.
        
        Args:
            issue_number: GitHub issue number
            agent_name: Name of agent taking ownership
            
        Returns:
            True if successfully marked, False if issue not found
        """
        for issue in self.current_queue:
            if issue.number == issue_number:
                issue.status = 'in_progress'
                issue.assigned_agent = agent_name
                print(f"✅ Issue #{issue_number} marked as in progress by {agent_name}")
                return True
        
        print(f"❌ Issue #{issue_number} not found in queue")
        return False
    
    def mark_issue_completed(self, issue_number: int) -> bool:
        """
        Mark issue as completed.
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            True if successfully marked, False if issue not found
        """
        for issue in self.current_queue:
            if issue.number == issue_number:
                issue.status = 'completed'
                self.completed_issues.add(issue_number)
                print(f"✅ Issue #{issue_number} marked as completed")
                return True
        
        print(f"❌ Issue #{issue_number} not found in queue")
        return False
    
    def get_queue_status(self) -> Dict[str, any]:
        """
        Get current status of the priority queue.
        
        Returns:
            Dictionary with queue statistics and issue breakdown
        """
        status_counts = {}
        priority_counts = {}
        
        for issue in self.current_queue:
            # Count by status
            status_counts[issue.status] = status_counts.get(issue.status, 0) + 1
            
            # Count by priority
            priority_name = issue.priority.name
            priority_counts[priority_name] = priority_counts.get(priority_name, 0) + 1
        
        return {
            "total_issues": len(self.current_queue),
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "completed_issues": list(self.completed_issues),
            "next_available": self.get_next_available_issue().number if self.get_next_available_issue() else None
        }
    
    def print_queue_summary(self):
        """Print a human-readable summary of the current queue."""
        print("\n📊 PRIORITY QUEUE STATUS")
        print("=" * 50)
        
        if not self.current_queue:
            print("📭 Queue is empty")
            return
        
        status = self.get_queue_status()
        
        print(f"Total issues: {status['total_issues']}")
        print(f"Next available: #{status['next_available']}" if status['next_available'] else "Next available: None")
        
        print("\n📈 By Priority:")
        for priority, count in status['priority_breakdown'].items():
            print(f"  {priority}: {count}")
        
        print("\n📋 By Status:")
        for status_name, count in status['status_breakdown'].items():
            print(f"  {status_name}: {count}")
        
        print("\n🎯 Top 5 Issues:")
        for i, issue in enumerate(self.current_queue[:5]):
            status_emoji = {
                'open': '🟢',
                'in_progress': '🟡', 
                'completed': '✅',
                'blocked': '🔴'
            }.get(issue.status, '⚪')
            
            deps_info = f" (deps: {issue.dependencies})" if issue.dependencies else ""
            print(f"  {i+1}. {status_emoji} #{issue.number} - {issue.title[:50]}...{deps_info}")