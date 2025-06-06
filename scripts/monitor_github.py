#!/usr/bin/env python3
"""
GitHub Monitoring Script for DigiNativa AI Team
==============================================

PURPOSE:
Continuously monitors GitHub Issues for new feature requests and
processes them automatically using the AI team.

USAGE:
    python scripts/monitor_github.py

This script should be run periodically (e.g., every 30 minutes) to
check for new feature requests from the project owner.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.projektledare import create_projektledare
from workflows.github_integration.project_owner_communication import ProjectOwnerCommunication

async def monitor_github_issues():
    """Main monitoring function."""
    print(f"🔍 Starting GitHub monitoring at {datetime.now()}")
    
    try:
        # Create Projektledare
        projektledare = create_projektledare()
        
        # Monitor and process issues
        results = await projektledare.monitor_and_process_github_issues()
        
        if results:
            print(f"✅ Successfully processed {len(results)} feature requests")
            for result in results:
                issue_num = result['request']['number']
                action = result['analysis']['recommendation']['action']
                print(f"   #{issue_num}: {action}")
        else:
            print("ℹ️  No new feature requests found")
            
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        return False
    
    return True

def main():
    """Run the monitoring script."""
    print("🤖 DigiNativa AI Team - GitHub Issue Monitor")
    print("=" * 50)
    
    success = asyncio.run(monitor_github_issues())
    
    if success:
        print("\n✅ Monitoring completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Monitoring failed")
        sys.exit(1)

if __name__ == "__main__":
    main()