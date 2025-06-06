"""
File Management Tools for DigiNativa AI Agents
==============================================

PURPOSE:
Provides AI agents with secure, validated file operations for reading project
DNA documents, creating specifications, writing reports, and managing artifacts.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import dataclasses

# FIXED: Use correct import for LangChain tools
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import PROJECT_ROOT, STATE_DIR

@dataclasses.dataclass
class FileOperation:
    """Record of a file operation for audit logging."""
    timestamp: datetime
    operation: str
    file_path: str
    agent_name: str
    success: bool
    error_message: Optional[str] = None
    file_size: Optional[int] = None

class FileOperationLogger:
    """Centralized logging for all file operations by AI agents."""
    def __init__(self):
        self.log_file = STATE_DIR / "logs" / "file_operations.json"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_operation(self, operation: FileOperation):
        """Log file operation to JSON file."""
        try:
            # Read existing logs
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new operation
            log_entry = {
                "timestamp": operation.timestamp.isoformat(),
                "operation": operation.operation,
                "file_path": operation.file_path,
                "agent_name": operation.agent_name,
                "success": operation.success,
                "error_message": operation.error_message,
                "file_size": operation.file_size
            }
            logs.append(log_entry)
            
            # Keep only last 1000 entries
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Write back to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️  Failed to log file operation: {e}")

file_logger = FileOperationLogger()

class FilePathValidator:
    """Validates file paths to prevent security issues."""
    ALLOWED_READ_PATHS = ["docs/", "config/", "templates/", "reports/", "tests/", "state/", "tools/", "agents/", "workflows/"]
    ALLOWED_WRITE_PATHS = ["reports/", "state/", "docs/specs/", "backend/", "src/", "tests/fixtures/"]
    ALLOWED_READ_EXTENSIONS = {'.md', '.txt', '.json', '.yml', '.yaml', '.toml', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.svg', '.csv', '.xml'}
    ALLOWED_WRITE_EXTENSIONS = {'.md', '.txt', '.json', '.yml', '.yaml', '.log', '.csv', '.html', '.svg', '.py', '.tsx', '.js', '.ts'}
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

    @classmethod
    def _validate_path(cls, file_path: Union[str, Path], allowed_paths: List[str], extensions: set, op: str) -> tuple[bool, str]:
        """Validate file path against security rules."""
        try:
            # Convert to Path and resolve
            path_obj = Path(file_path)
            
            # Handle both absolute and relative paths
            if path_obj.is_absolute():
                try:
                    relative_path = path_obj.relative_to(PROJECT_ROOT.resolve())
                except ValueError:
                    return False, f"Path outside project directory: {file_path}"
            else:
                relative_path = path_obj
                path_obj = PROJECT_ROOT / relative_path
            
            # Convert to forward slashes for consistent checking
            relative_path_str = str(relative_path).replace('\\', '/')
            
            # Check if path starts with allowed directory
            if not any(relative_path_str.startswith(allowed) for allowed in allowed_paths):
                return False, f"Path not in allowed {op} directories: {file_path}. Allowed: {allowed_paths}"
            
            # Check file extension
            if path_obj.suffix.lower() not in extensions:
                return False, f"File extension not allowed for {op}: {path_obj.suffix}. Allowed: {extensions}"
            
            # For write operations, create parent directory
            if op == "write":
                path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # For read operations, check file exists
            if op == "read" and not path_obj.exists():
                return False, f"File does not exist: {file_path}"
            
            # Check file size if exists
            if path_obj.exists() and path_obj.stat().st_size > cls.MAX_FILE_SIZE_BYTES:
                size_mb = path_obj.stat().st_size / (1024 * 1024)
                return False, f"File too large: {file_path} ({size_mb:.1f}MB > 10MB limit)"
            
            return True, ""
            
        except Exception as e:
            return False, f"Path validation error for {file_path}: {e}"

    @classmethod
    def validate_read_path(cls, fp: Union[str, Path]) -> tuple[bool, str]:
        return cls._validate_path(fp, cls.ALLOWED_READ_PATHS, cls.ALLOWED_READ_EXTENSIONS, "read")
    
    @classmethod
    def validate_write_path(cls, fp: Union[str, Path]) -> tuple[bool, str]:
        return cls._validate_path(fp, cls.ALLOWED_WRITE_PATHS, cls.ALLOWED_WRITE_EXTENSIONS, "write")

class FileReadInput(BaseModel):
    """Input model for file reading operations."""
    file_path: str = Field(..., description="Path to the file to read")
    agent_name: str = Field(default="unknown", description="Name of the agent performing the operation")

class FileWriteInput(BaseModel):
    """Input model for file writing operations."""
    file_path: str = Field(..., description="Path to save the file", alias="filepath")
    content: str = Field(..., description="Content to write to the file")
    agent_name: str = Field(default="unknown", description="Name of the agent performing the operation")

class FileReadTool(BaseTool):
    """Tool for safely reading files."""
    name: str = "file_read_tool"
    description: str = "Read the contents of a file safely with proper validation and logging."
    args_schema: type[BaseModel] = FileReadInput
    
    def _run(self, file_path: str, agent_name: str = "unknown") -> str:
        """Execute file reading operation."""
        return read_file(file_path=file_path, agent_name=agent_name)

class FileWriteTool(BaseTool):
    """Tool for safely writing files."""
    name: str = "file_write_tool"
    description: str = "Write content to a file safely with proper validation and logging."
    args_schema: type[BaseModel] = FileWriteInput
    
    def _run(self, file_path: str, content: str, agent_name: str = "unknown") -> str:
        """Execute file writing operation."""
        return write_file(file_path=file_path, content=content, agent_name=agent_name)

def read_file(file_path: str, agent_name: str = "unknown", encoding: str = "utf-8") -> str:
    """
    Convenience function to read a file directly with full validation and logging.
    
    Args:
        file_path: Path to the file to read
        agent_name: Name of the agent requesting the operation
        encoding: File encoding (default: utf-8)
    
    Returns:
        File contents as string, or error message if operation fails
    """
    start_time = datetime.now()
    
    try:
        # Validate path
        is_valid, error_msg = FilePathValidator.validate_read_path(file_path)
        if not is_valid:
            file_logger.log_operation(FileOperation(
                timestamp=start_time,
                operation="read",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            return f"❌ File read error: {error_msg}"

        # Read file
        resolved_path = Path(file_path).resolve()
        with open(resolved_path, 'r', encoding=encoding) as file:
            content = file.read()
        
        # Log successful operation
        file_logger.log_operation(FileOperation(
            timestamp=start_time,
            operation="read",
            file_path=str(resolved_path),
            agent_name=agent_name,
            success=True,
            file_size=len(content)
        ))
        
        return content
        
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        file_logger.log_operation(FileOperation(
            timestamp=start_time,
            operation="read",
            file_path=file_path,
            agent_name=agent_name,
            success=False,
            error_message=error_msg
        ))
        return f"❌ {error_msg}"

def write_file(file_path: str, content: str, agent_name: str = "unknown", 
               encoding: str = "utf-8", create_backup: bool = True) -> str:
    """
    Convenience function to write a file directly with full validation and logging.
    
    Args:
        file_path: Path where to save the file
        content: Content to write
        agent_name: Name of the agent requesting the operation
        encoding: File encoding (default: utf-8)
        create_backup: Whether to create backup of existing file
    
    Returns:
        Success message or error message if operation fails
    """
    start_time = datetime.now()
    
    try:
        # Validate path
        is_valid, error_msg = FilePathValidator.validate_write_path(file_path)
        if not is_valid:
            file_logger.log_operation(FileOperation(
                timestamp=start_time,
                operation="write",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            return f"❌ File write error: {error_msg}"

        # Resolve path and create directories
        resolved_path = Path(file_path).resolve()
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if file exists and backup is requested
        if create_backup and resolved_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = resolved_path.parent / f"{resolved_path.stem}_{timestamp}_backup{resolved_path.suffix}"
            shutil.copy2(resolved_path, backup_path)
        
        # Write file
        with open(resolved_path, 'w', encoding=encoding) as file:
            file.write(content)
        
        # Log successful operation
        file_logger.log_operation(FileOperation(
            timestamp=start_time,
            operation="write",
            file_path=str(resolved_path),
            agent_name=agent_name,
            success=True,
            file_size=len(content)
        ))
        
        return f"✅ File written successfully to {resolved_path}"
        
    except Exception as e:
        error_msg = f"Error writing file {file_path}: {str(e)}"
        file_logger.log_operation(FileOperation(
            timestamp=start_time,
            operation="write", 
            file_path=file_path,
            agent_name=agent_name,
            success=False,
            error_message=error_msg
        ))
        return f"❌ {error_msg}"

def list_files_in_directory(directory_path: str, agent_name: str = "unknown", 
                          extension_filter: Optional[str] = None) -> str:
    """
    List files in a directory with optional extension filtering.
    
    Args:
        directory_path: Path to directory to list
        agent_name: Name of requesting agent
        extension_filter: Optional file extension to filter by (e.g., '.md', '.py')
    
    Returns:
        JSON string with file list or error message
    """
    try:
        # Validate directory path
        dir_path = Path(directory_path)
        if not dir_path.exists():
            return f"❌ Directory does not exist: {directory_path}"
        
        if not dir_path.is_dir():
            return f"❌ Path is not a directory: {directory_path}"
        
        # List files
        files = []
        for file_path in dir_path.iterdir():
            if file_path.is_file():
                if extension_filter is None or file_path.suffix.lower() == extension_filter.lower():
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path.relative_to(PROJECT_ROOT)),
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
        
        result = {
            "directory": directory_path,
            "file_count": len(files),
            "files": files
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"❌ Error listing directory {directory_path}: {str(e)}"