#!/usr/bin/env python3
"""
Test Project Repository Workflow
==============================

Tests the new workflow where features are created in project repo
and stories are linked as child issues.
"""

import asyncio
from datetime import datetime

async def test_project_repo_workflow():
    """Test complete project repo workflow."""
    
    print("🧪 Testing Project Repository Workflow")
    print("="*60)
    
    try:
        # Step 1: Initialize Projektledare
        from agents.projektledare import create_projektledare
        projektledare = create_projektledare()
        
        # Step 2: Monitor project repo for features
        print("\n🔍 Step 1: Monitor project repo for features")
        features = await projektledare.monitor_project_repo_features()
        
        if features:
            print(f"✅ Found {len(features)} features in project repo")
            
            for feature in features:
                print(f"  📋 Feature #{feature['request']['number']}: {feature['request']['title']}")
                if feature.get('story_issues'):
                    print(f"    📝 Created {len(feature['story_issues'])} linked stories")
        else:
            print("ℹ️  No features found - create one in diginativa-game repo!")
            print("💡 Create GitHub Issue in diginativa-game with labels: 'feature', 'enhancement'")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_project_repo_workflow())
    
    if success:
        print("\n🎉 Project repo workflow test completed!")
    else:
        print("\n❌ Test failed - check configuration")#!/usr/bin/env python3
"""
Test Project Repository Workflow
==============================

Tests the new workflow where features are created in project repo
and stories are linked as child issues.
"""

import asyncio
from datetime import datetime

async def test_project_repo_workflow():
    """Test complete project repo workflow."""
    
    print("🧪 Testing Project Repository Workflow")
    print("="*60)
    
    try:
        # Step 1: Initialize Projektledare
        from agents.projektledare import create_projektledare
        projektledare = create_projektledare()
        
        # Step 2: Monitor project repo for features
        print("\n🔍 Step 1: Monitor project repo for features")
        features = await projektledare.monitor_project_repo_features()
        
        if features:
            print(f"✅ Found {len(features)} features in project repo")
            
            for feature in features:
                print(f"  📋 Feature #{feature['request']['number']}: {feature['request']['title']}")
                if feature.get('story_issues'):
                    print(f"    📝 Created {len(feature['story_issues'])} linked stories")
        else:
            print("ℹ️  No features found - create one in diginativa-game repo!")
            print("💡 Create GitHub Issue in diginativa-game with labels: 'feature', 'enhancement'")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_project_repo_workflow())
    
    if success:
        print("\n🎉 Project repo workflow test completed!")
    else:
        print("\n❌ Test failed - check configuration")