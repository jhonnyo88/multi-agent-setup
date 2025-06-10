"""
Simple File Utilities for DigiNativa AI Team
==========================================

PURPOSE:
Simplified file operations without complex tool inheritance.
Replaces the overcomplicated tool system with simple functions.

ADAPTATION GUIDE:
🔧 To adapt for your project:
1. Update ALLOWED_PATHS for your directory structure
2. Modify file extension restrictions for your file types
3. Adjust security validation for your requirements
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Project configuration
PROJECT_ROOT = Path(__file__).parent.parent
ALLOWED_READ_PATHS = ["docs/", "config/", "agents/", "workflows/", "tools/"]
ALLOWED_WRITE_PATHS = ["docs/specs/", "reports/", "backend/", "frontend/"]

def read_file(file_path: str) -> str:
    """
    Simple file reading with basic validation.
    
    Args:
        file_path: Path to file (relative to project root)
        
    Returns:
        File content as string, or error message if failed
    """
    try:
        # Convert to absolute path
        if not Path(file_path).is_absolute():
            full_path = PROJECT_ROOT / file_path
        else:
            full_path = Path(file_path)
        
        # Basic security check
        if not _is_safe_read_path(file_path):
            return f"❌ Path not allowed for reading: {file_path}"
        
        # Read file
        if not full_path.exists():
            return f"❌ File not found: {file_path}"
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Read file: {file_path}")
        return content
        
    except Exception as e:
        return f"❌ Error reading {file_path}: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """
    Simple file writing with basic validation.
    
    Args:
        file_path: Path where to save file
        content: Content to write
        
    Returns:
        Success/error message
    """
    try:
        # Convert to absolute path
        if not Path(file_path).is_absolute():
            full_path = PROJECT_ROOT / file_path
        else:
            full_path = Path(file_path)
        
        # Basic security check
        if not _is_safe_write_path(file_path):
            return f"❌ Path not allowed for writing: {file_path}"
        
        # Create directory if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Wrote file: {file_path}")
        return f"✅ File written successfully: {file_path}"
        
    except Exception as e:
        return f"❌ Error writing {file_path}: {str(e)}"

def list_files(directory_path: str, extension: Optional[str] = None) -> List[str]:
    """
    List files in a directory.
    
    Args:
        directory_path: Directory to list
        extension: Optional file extension filter (e.g., '.py', '.md')
        
    Returns:
        List of file paths
    """
    try:
        # Convert to absolute path
        if not Path(directory_path).is_absolute():
            full_path = PROJECT_ROOT / directory_path
        else:
            full_path = Path(directory_path)
        
        if not full_path.exists() or not full_path.is_dir():
            return []
        
        files = []
        for item in full_path.iterdir():
            if item.is_file():
                if extension is None or item.suffix.lower() == extension.lower():
                    # Return path relative to project root
                    try:
                        rel_path = item.relative_to(PROJECT_ROOT)
                        files.append(str(rel_path).replace('\\', '/'))
                    except ValueError:
                        # File outside project root
                        continue
        
        return sorted(files)
        
    except Exception as e:
        print(f"❌ Error listing {directory_path}: {e}")
        return []

def save_json(file_path: str, data: Dict[str, Any]) -> str:
    """Save data as JSON file."""
    try:
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        return write_file(file_path, json_content)
    except Exception as e:
        return f"❌ Error saving JSON: {str(e)}"

def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON file."""
    try:
        content = read_file(file_path)
        if content.startswith("❌"):
            return None
        return json.loads(content)
    except Exception as e:
        print(f"❌ Error loading JSON {file_path}: {e}")
        return None

def _is_safe_read_path(file_path: str) -> bool:
    """Check if path is safe for reading."""
    path_str = str(file_path).replace('\\', '/')
    return any(path_str.startswith(allowed) for allowed in ALLOWED_READ_PATHS)

def _is_safe_write_path(file_path: str) -> bool:
    """Check if path is safe for writing."""
    path_str = str(file_path).replace('\\', '/')
    return any(path_str.startswith(allowed) for allowed in ALLOWED_WRITE_PATHS)

# Convenience functions for common operations
def read_spec_file(story_id: str) -> str:
    """Read a specification file for a story."""
    possible_paths = [
        f"docs/specs/spec-{story_id}.md",
        f"docs/specs/spec_{story_id}.md",
        f"docs/specs/{story_id}-spec.md"
    ]
    
    for path in possible_paths:
        content = read_file(path)
        if not content.startswith("❌"):
            return content
    
    return f"❌ No specification found for {story_id}"

def save_spec_file(story_id: str, content: str) -> str:
    """Save a specification file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = f"docs/specs/spec-{story_id}-{timestamp}.md"
    return write_file(file_path, content)

def get_project_structure(max_depth: int = 2) -> str:
    """Get overview of project structure."""
    structure = []
    
    def add_directory(path: Path, prefix: str = "", depth: int = 0):
        if depth >= max_depth:
            return
        
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for i, item in enumerate(items):
                # Skip hidden files and common ignored directories
                if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules']:
                    continue
                
                is_last = i == len([x for x in items if not x.name.startswith('.')]) - 1
                current_prefix = "└── " if is_last else "├── "
                
                if item.is_dir():
                    structure.append(f"{prefix}{current_prefix}📁 {item.name}/")
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    add_directory(item, next_prefix, depth + 1)
                else:
                    # Only show important file types
                    if item.suffix in ['.py', '.md', '.json', '.yml', '.toml', '.txt']:
                        structure.append(f"{prefix}{current_prefix}📄 {item.name}")
        
        except PermissionError:
            structure.append(f"{prefix}❌ Permission denied")
    
    structure.append(f"📁 {PROJECT_ROOT.name}/ (Project Root)")
    add_directory(PROJECT_ROOT)
    
    return "\n".join(structure)

# Test functions
def test_file_operations():
    """Test basic file operations."""
    print("🧪 Testing file operations...")
    
    # Test reading existing file
    config_content = read_file("config/settings.py")
    if not config_content.startswith("❌"):
        print("✅ Read operation successful")
    else:
        print(f"❌ Read test failed: {config_content}")
    
    # Test listing files
    py_files = list_files("agents", ".py")
    print(f"✅ Found {len(py_files)} Python files in agents/")
    
    # Test project structure
    structure = get_project_structure(2)
    print("✅ Project structure generated")
    
    print("🎉 File operations test complete!")

if __name__ == "__main__":
    test_file_operations()