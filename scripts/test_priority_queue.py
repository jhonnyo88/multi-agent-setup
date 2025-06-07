# scripts/test_priority_queue.py
#!/usr/bin/env python3
"""
Test Priority Queue Implementation
================================

Tests the new priority queue functionality in Projektledare.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.projektledare import create_projektledare

async def test_priority_queue():
    """Test the priority queue functionality."""
    print("🧪 Testing Priority Queue Implementation")
    print("=" * 50)
    
    try:
        # Create Projektledare
        projektledare = create_projektledare()
        
        # Test 1: Get next available feature
        print("\n📋 Test 1: Getting next available feature...")
        next_feature = await projektledare.get_next_available_feature()
        
        if next_feature:
            print(f"✅ Found feature: #{next_feature['number']} - {next_feature['title']}")
            
            # Test priority parsing
            priority = projektledare._get_issue_priority(next_feature)
            print(f"   Priority: {priority}")
            
            # Test dependency parsing
            deps = projektledare._parse_dependencies(next_feature.get('body', ''))
            print(f"   Dependencies: {deps}")
            
        else:
            print("ℹ️  No features available (expected if no open issues)")
        
        # Test 2: Priority sorting
        print("\n🔢 Test 2: Testing priority sorting...")
        
        # Mock issues for testing
        mock_issues = [
            {'number': 1, 'title': 'Low priority', 'labels': [{'name': 'priority-p3'}]},
            {'number': 2, 'title': 'Critical issue', 'labels': [{'name': 'priority-p0'}]},
            {'number': 3, 'title': 'Medium priority', 'labels': [{'name': 'priority-p2'}]},
            {'number': 4, 'title': 'High priority', 'labels': [{'name': 'priority-p1'}]},
        ]
        
        sorted_issues = projektledare._sort_by_priority(mock_issues)
        
        print("   Sorted order:")
        for i, issue in enumerate(sorted_issues):
            priority = projektledare._get_issue_priority(issue)
            print(f"   {i+1}. #{issue['number']}: {issue['title']} ({priority})")
        
        # Verify correct order
        expected_order = [2, 4, 3, 1]  # P0, P1, P2, P3
        actual_order = [issue['number'] for issue in sorted_issues]
        
        if actual_order == expected_order:
            print("   ✅ Priority sorting works correctly")
        else:
            print(f"   ❌ Priority sorting failed. Expected: {expected_order}, Got: {actual_order}")
        
        # Test 3: Dependency parsing
        print("\n🔗 Test 3: Testing dependency parsing...")
        
        test_bodies = [
            "Dependencies: #123, #124",
            "Depends on: #456",
            "Requires #789 to be completed first",
            "This feature needs #111 and #222 before starting",
            "No dependencies mentioned here"
        ]
        
        for body in test_bodies:
            deps = projektledare._parse_dependencies(body)
            print(f"   '{body[:30]}...' → {deps}")
        
        print("\n✅ Priority Queue implementation test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_priority_queue())