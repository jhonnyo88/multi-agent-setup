#!/usr/bin/env python3
"""
GitHub Integration Connection Tests
==================================

Tests for verifying GitHub API connection and basic functionality.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_github_integration_import():
    """Test that we can import GitHub integration modules."""
    # This should not raise any ImportError
    from workflows.github_integration.project_owner_communication import GitHubIntegration
    from workflows.github_integration import ProjectOwnerCommunication
    
    # Assertions for pytest
    assert GitHubIntegration is not None
    assert ProjectOwnerCommunication is not None


def test_github_connection_with_invalid_token():
    """Test GitHub API connection with invalid/missing token - should handle gracefully."""
    from workflows.github_integration.project_owner_communication import GitHubIntegration
    
    # We expect this to fail with 401 or configuration error
    with pytest.raises((ValueError, Exception)) as exc_info:
        GitHubIntegration()
    
    # Verify it's the expected authentication/configuration error
    error_msg = str(exc_info.value)
    assert ("401" in error_msg or 
            "Bad credentials" in error_msg or 
            "not configured" in error_msg)


@patch('workflows.github_integration.project_owner_communication.SECRETS')
@patch('workflows.github_integration.project_owner_communication.Github')
def test_github_mock_connection(mock_github_class, mock_secrets):
    """Test GitHub integration with mocked connection."""
    # Mock the secrets
    mock_secrets.get.return_value = 'mock_valid_token'
    
    # Mock the GitHub API
    mock_repo = MagicMock()
    mock_repo.owner = "jhonnyo88"
    mock_repo.name = "multi-agent-setup"
    
    mock_github_instance = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github_class.return_value = mock_github_instance
    
    # Import and test
    from workflows.github_integration.project_owner_communication import GitHubIntegration
    
    # This should work with mocked dependencies
    gh_integration = GitHubIntegration()
    
    # Assertions
    assert gh_integration is not None
    assert gh_integration.repo_owner == "jhonnyo88"
    assert gh_integration.repo_name == "multi-agent-setup"
    assert gh_integration.github == mock_github_instance
    
    # Verify the GitHub class was called with correct auth
    mock_github_class.assert_called_once_with('mock_valid_token')


@patch('workflows.github_integration.project_owner_communication.SECRETS')
@patch('workflows.github_integration.project_owner_communication.Github')
def test_project_owner_communication(mock_github_class, mock_secrets):
    """Test ProjectOwnerCommunication class initialization."""
    # Mock dependencies
    mock_secrets.get.return_value = 'mock_valid_token'
    mock_github_instance = MagicMock()
    mock_repo = MagicMock()
    mock_github_instance.get_repo.return_value = mock_repo
    mock_github_class.return_value = mock_github_instance
    
    # Import and test
    from workflows.github_integration.project_owner_communication import ProjectOwnerCommunication
    
    # This should work with mocked dependencies
    comm = ProjectOwnerCommunication()
    
    # Assertions
    assert comm is not None
    assert comm.github is not None
    assert comm.status_handler is not None


# Integration test function for manual running
def run_manual_tests():
    """Run tests manually with detailed output (for debugging)."""
    print("🧪 Running Manual GitHub Integration Tests...")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Import test
    print("\n🔍 Test 1: Import Test")
    try:
        test_github_integration_import()
        print("   ✅ PASS - All imports successful")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
    tests_total += 1
    
    # Test 2: Connection test (expecting failure)
    print("\n🔍 Test 2: Connection Test (expecting auth failure)")
    try:
        test_github_connection_with_invalid_token()
        print("   ✅ PASS - Authentication error handled correctly")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
    tests_total += 1
    
    # Test 3: Mock test
    print("\n🔍 Test 3: Mock Connection Test")
    try:
        with patch('workflows.github_integration.project_owner_communication.SECRETS') as mock_secrets, \
             patch('workflows.github_integration.project_owner_communication.Github') as mock_github:
            
            mock_secrets.get.return_value = 'mock_token'
            mock_repo = MagicMock()
            mock_github.return_value.get_repo.return_value = mock_repo
            
            from workflows.github_integration.project_owner_communication import GitHubIntegration
            gh = GitHubIntegration()
            
            assert gh is not None
            print("   ✅ PASS - Mock connection successful")
            tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
    tests_total += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {tests_passed}/{tests_total} tests passed")
    
    return tests_passed == tests_total


if __name__ == "__main__":
    # When run directly, use manual test runner
    success = run_manual_tests()
    sys.exit(0 if success else 1)