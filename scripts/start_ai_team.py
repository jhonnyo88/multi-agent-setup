"""
DigiNativa AI-Team Main Entry Point
===================================

PURPOSE:
Main entry point for starting the AI team. Runs priority queue loop
and coordinates agent chain according to target workflow.

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Line 45-60: Update agent registry for your specific agents
2. Line 80-100: Modify main loop timing for your workflow
3. Line 120-150: Adapt error handling for your environment
4. Line 200-220: Update notification system for your communication

USAGE:
python scripts/start_ai_team.py

CONFIGURATION POINTS:
- Line 55: Agent registry setup
- Line 95: Main loop interval
- Line 160: Error recovery strategy
"""

import asyncio
import sys
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import DigiNativa components
from workflows.priority_queue import PriorityQueueManager, Priority
from workflows.agent_coordinator import AgentChainCoordinator, AgentType
from workflows.github_integration.project_owner_communication import ProjectOwnerCommunication
from config.settings import GITHUB_CONFIG, AGENT_CONFIG

# Import agents (these will be implemented step by step)
try:
    from agents.projektledare import ProjektledareAgent
    from agents.speldesigner import SpeldesignerAgent
    from agents.utvecklare_backend import UtvecklareBackendAgent
    from agents.utvecklare_frontend import UtvecklareFrontendAgent
    from agents.testutvecklare import TestutvecklareAgent
    from agents.qa_testare import QATestareAgent
    from agents.kvalitetsgranskare import KvalitetsgranskarAgent
except ImportError as e:
    print(f"⚠️ Some agents not yet implemented: {e}")
    print("   Will use mock agents for testing")

class AITeamOrchestrator:
    """
    Main orchestrator for the DigiNativa AI team.
    
    RESPONSIBILITIES:
    1. Initialize all components (priority queue, agents, GitHub integration)
    2. Run main execution loop
    3. Handle errors and recovery
    4. Coordinate communication with project owner
    5. Monitor and report system health
    """
    
    def __init__(self):
        self.running = False
        self.github_comm = None
        self.priority_queue = None
        self.agent_coordinator = None
        self.projektledare = None
        self.agents_registry = {}
        
    async def initialize(self) -> bool:
        """
        Initialize all AI team components.
        
        INITIALIZATION PROCESS:
        1. Setup GitHub communication
        2. Initialize priority queue manager
        3. Setup agent registry
        4. Initialize agent coordinator
        5. Validate configuration
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            print("🚀 Initializing DigiNativa AI-Team...")
            
            # Initialize GitHub communication
            print("   📡 Setting up GitHub integration...")
            self.github_comm = ProjectOwnerCommunication()
            
            # Test GitHub connection
            if not await self._test_github_connection():
                return False
            
            # Initialize priority queue
            print("   📋 Setting up Priority Queue...")
            self.priority_queue = PriorityQueueManager(self.github_comm.github)
            
            # Initialize agents registry
            print("   🤖 Setting up Agent Registry...")
            self.agents_registry = await self._setup_agents_registry()
            
            # Initialize agent coordinator
            print("   🎯 Setting up Agent Coordinator...")
            self.agent_coordinator = AgentChainCoordinator(self.agents_registry)
            
            # Initialize projektledare (main orchestrator agent)
            print("   👨‍💼 Setting up Projektledare...")
            self.projektledare = ProjektledareAgent()
            
            print("✅ AI-Team initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _test_github_connection(self) -> bool:
        """Test GitHub API connection."""
        try:
            # Try to fetch repository information
            repo_info = await self.github_comm.github.get_repository_info()
            print(f"   ✅ Connected to GitHub repo: {repo_info.get('name', 'Unknown')}")
            return True
        except Exception as e:
            print(f"   ❌ GitHub connection failed: {e}")
            print("   Please check your GITHUB_TOKEN in .env file")
            return False
    
    async def _setup_agents_registry(self) -> Dict[AgentType, Any]:
        """
        Setup the agent registry with all available agents.
        
        AGENT INITIALIZATION STRATEGY:
        1. Try to import and initialize each agent
        2. If agent not implemented, use mock agent
        3. Log which agents are available vs mocked
        4. Return complete registry
        
        Returns:
            Dictionary mapping AgentType to agent instances
        """
        registry = {}
        
        # Agent initialization mapping
        agent_classes = {
            AgentType.SPELDESIGNER: ('SpeldesignerAgent', SpeldesignerAgent if 'SpeldesignerAgent' in globals() else None),
            AgentType.UTVECKLARE_BACKEND: ('UtvecklareBackendAgent', UtvecklareBackendAgent if 'UtvecklareBackendAgent' in globals() else None),
            AgentType.UTVECKLARE_FRONTEND: ('UtvecklareFrontendAgent', UtvecklareFrontendAgent if 'UtvecklareFrontendAgent' in globals() else None),
            AgentType.TESTUTVECKLARE: ('TestutvecklareAgent', TestutvecklareAgent if 'TestutvecklareAgent' in globals() else None),
            AgentType.QA_TESTARE: ('QATestareAgent', QATestareAgent if 'QATestareAgent' in globals() else None),
            AgentType.KVALITETSGRANSKARE: ('KvalitetsgranskarAgent', KvalitetsgranskarAgent if 'KvalitetsgranskarAgent' in globals() else None)
        }
        
        for agent_type, (class_name, agent_class) in agent_classes.items():
            try:
                if agent_class:
                    # Real agent available
                    registry[agent_type] = agent_class()
                    print(f"   ✅ {agent_type.value}: Real agent initialized")
                else:
                    # Use mock agent
                    registry[agent_type] = MockAgent(agent_type)
                    print(f"   🎭 {agent_type.value}: Mock agent (implementation pending)")
                    
            except Exception as e:
                print(f"   ⚠️ {agent_type.value}: Failed to initialize, using mock - {e}")
                registry[agent_type] = MockAgent(agent_type)
        
        return registry
    
    async def run_main_loop(self):
        """
        Main execution loop for the AI team.
        
        LOOP LOGIC:
        1. Refresh priority queue from GitHub
        2. Find next available issue (highest priority, no blocking deps)
        3. Analyze feature with projektledare
        4. Create and execute agent chain
        5. Handle results and notify project owner
        6. Handle errors and recovery
        7. Repeat with configurable interval
        """
        print("🔄 Starting main AI team execution loop...")
        self.running = True
        
        loop_count = 0
        
        while self.running:
            try:
                loop_count += 1
                print(f"\n🔍 Loop #{loop_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Step 1: Refresh priority queue
                await self.priority_queue.refresh_queue()
                current_queue = self.priority_queue.current_queue
                
                if not current_queue:
                    print("📭 No issues in queue, waiting...")
                    await asyncio.sleep(AGENT_CONFIG.get('queue_check_interval', 60))
                    continue
                
                # Print queue summary for visibility
                self.priority_queue.print_queue_summary()
                
                # Step 2: Find next available issue
                next_issue = self.priority_queue.get_next_available_issue()
                
                if not next_issue:
                    print("⏸️ All issues blocked by dependencies, waiting...")
                    await asyncio.sleep(AGENT_CONFIG.get('dependency_check_interval', 30))
                    continue
                
                print(f"\n🎯 Processing: #{next_issue.number} - {next_issue.title}")
                print(f"   Priority: {next_issue.priority.name}")
                if next_issue.dependencies:
                    print(f"   Dependencies (satisfied): {next_issue.dependencies}")
                
                # Step 3: Mark as in progress
                self.priority_queue.mark_issue_in_progress(next_issue.number, "AI-Team")
                
                # Step 4: Analyze feature with projektledare
                print("   🔍 Analyzing feature with Projektledare...")
                feature_analysis = await self.projektledare.analyze_feature_request(next_issue.number)
                
                # Check if feature is approved for development
                recommendation = feature_analysis.get("recommendation", {})
                action = recommendation.get("action", "").upper()
                
                if action != "APPROVE":
                    print(f"   ❌ Feature not approved: {recommendation.get('reasoning', 'No reason given')}")
                    
                    # Post analysis results to GitHub
                    await self.github_comm.post_ai_analysis_comment(
                        next_issue.number, 
                        feature_analysis
                    )
                    continue
                
                print("   ✅ Feature approved for development")
                
                # Step 5: Create agent chain
                print("   📋 Creating agent chain...")
                agent_chain = self.agent_coordinator.create_agent_chain_for_feature(
                    next_issue.number, 
                    feature_analysis
                )
                
                # Step 6: Execute agent chain
                print("   🏃‍♂️ Executing agent chain...")
                chain_result = await self.agent_coordinator.execute_agent_chain(next_issue.number)
                
                # Step 7: Handle results
                if chain_result.overall_status == "completed":
                    print(f"   ✅ Feature #{next_issue.number} completed successfully!")
                    
                    # Mark as completed in priority queue
                    self.priority_queue.mark_issue_completed(next_issue.number)
                    
                    # Notify project owner
                    await self.github_comm.post_feature_completed_notification(
                        next_issue.number, 
                        chain_result
                    )
                    
                elif chain_result.overall_status == "failed":
                    print(f"   ❌ Feature #{next_issue.number} failed: {chain_result.error_details}")
                    
                    # Escalate to project owner
                    await self.github_comm.post_error_escalation(
                        next_issue.number,
                        chain_result.error_details,
                        chain_result
                    )
                    
                else:
                    print(f"   ⚠️ Feature #{next_issue.number} in unexpected state: {chain_result.overall_status}")
                
                # Brief pause between iterations
                await asyncio.sleep(AGENT_CONFIG.get('loop_interval', 10))
                
            except KeyboardInterrupt:
                print("\n🛑 Graceful shutdown requested...")
                self.running = False
                break
                
            except Exception as e:
                print(f"   🚨 Error in main loop: {e}")
                
                # Log detailed error for debugging
                import traceback
                traceback.print_exc()
                
                # Continue after error with longer pause
                await asyncio.sleep(AGENT_CONFIG.get('error_recovery_interval', 30))
        
        print("🏁 AI team execution loop stopped")
    
    async def shutdown(self):
        """Graceful shutdown of AI team."""
        print("🛑 Shutting down AI team...")
        self.running = False
        
        # Add any cleanup logic here
        # - Save state
        # - Close connections
        # - Notify ongoing processes
        
        print("✅ AI team shutdown complete")

class MockAgent:
    """
    Mock agent for testing when real agents aren't implemented yet.
    
    Simulates agent behavior to test the coordination system
    without requiring full agent implementation.
    """
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        
    async def execute_task(self, task) -> Dict[str, Any]:
        """
        Mock task execution.
        
        Simulates successful completion with mock deliverables.
        """
        print(f"     🎭 Mock {self.agent_type.value}: Simulating task execution...")
        
        # Simulate work time
        await asyncio.sleep(1)
        
        # Return mock success result
        return {
            "success": True,
            "data": {
                "agent_type": self.agent_type.value,
                "task_id": task.story_id,
                "execution_time": "1 second (simulated)"
            },
            "deliverables": {
                "mock_deliverable": f"Mock output from {self.agent_type.value}",
                "task_description": task.description
            }
        }

async def main():
    """Main entry point for the AI team."""
    orchestrator = AITeamOrchestrator()
    
    # Setup graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🔔 Received signal {signum}, initiating shutdown...")
        asyncio.create_task(orchestrator.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize components
        if not await orchestrator.initialize():
            print("❌ Failed to initialize AI team")
            return 1
        
        # Start main execution loop
        await orchestrator.run_main_loop()
        
        return 0
        
    except Exception as e:
        print(f"🚨 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await orchestrator.shutdown()

if __name__ == "__main__":
    print("🚀 DigiNativa AI-Team Starting...")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Project root: {project_root}")
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)