#!/usr/bin/env python3
"""
Debug GitHub Issue Search
========================
"""

import asyncio
from workflows.github_integration.project_owner_communication import ProjectOwnerCommunication

async def debug_issue_search():
    """Debug varför issue #12 inte hittas."""
    
    print("🔍 Debug: GitHub Issue Search")
    
    try:
        # Skapa GitHub communication
        github_comm = ProjectOwnerCommunication()
        
        print(f"✅ GitHub authenticated")
        print(f"   AI repo: {github_comm.github.ai_repo.full_name}")
        print(f"   Project repo: {github_comm.github.project_repo.full_name}")
        
        # Sök i båda repositories
        print("\n🔍 Searching in AI repository (multi-agent-setup):")
        ai_issues = list(github_comm.github.ai_repo.get_issues(
            state='open',
            labels=['enhancement', 'ai-team']
        ))
        print(f"   Found {len(ai_issues)} issues")
        for issue in ai_issues:
            print(f"   #{issue.number}: {issue.title}")
        
        print("\n🔍 Searching in Project repository (diginativa-game):")
        project_issues = list(github_comm.github.project_repo.get_issues(
            state='open',
            labels=['enhancement', 'ai-team']
        ))
        print(f"   Found {len(project_issues)} issues")
        for issue in project_issues:
            print(f"   #{issue.number}: {issue.title}")
        
        # Sök specifikt efter issue #12
        print("\n🔍 Looking specifically for issue #12:")
        try:
            issue_12 = github_comm.github.project_repo.get_issue(12)
            print(f"   ✅ Found issue #12: {issue_12.title}")
            print(f"   State: {issue_12.state}")
            print(f"   Labels: {[label.name for label in issue_12.labels]}")
            
            # Kontrollera om den har rätt labels
            label_names = [label.name for label in issue_12.labels]
            has_enhancement = 'enhancement' in label_names
            has_ai_team = 'ai-team' in label_names
            
            print(f"   Has 'enhancement': {has_enhancement}")
            print(f"   Has 'ai-team': {has_ai_team}")
            
            if has_enhancement and has_ai_team:
                print("   ✅ Issue #12 should be detected by AI team")
            else:
                print("   ❌ Issue #12 missing required labels")
                if not has_enhancement:
                    print("     Missing: 'enhancement' label")
                if not has_ai_team:
                    print("     Missing: 'ai-team' label")
                    
        except Exception as e:
            print(f"   ❌ Could not find issue #12: {e}")
        
        # Test AI analysis detection
        print("\n🔍 Checking for existing AI analysis:")
        if project_issues:
            for issue in project_issues:
                has_analysis = await github_comm.github._check_for_ai_analysis(issue)
                print(f"   #{issue.number}: Has AI analysis: {has_analysis}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_issue_search())