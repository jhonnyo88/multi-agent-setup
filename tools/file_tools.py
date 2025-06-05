"""
File Management Tools for DigiNativa AI Agents
==============================================

PURPOSE:
Provides AI agents with secure, validated file operations for reading project
DNA documents, creating specifications, writing reports, and managing artifacts.

ADAPTATION GUIDE:
🔧 To adapt these tools for your project:
1. Line 50-70: Update ALLOWED_PATHS for your project structure
2. Line 100-120: Modify file validation rules for your file types
3. Line 200-250: Adjust backup and versioning strategy for your needs
4. Line 300-350: Update security restrictions for your environment

SECURITY FEATURES:
- Path validation prevents directory traversal attacks
- File type validation ensures only approved formats
- Size limits prevent resource exhaustion
- Automatic backup of modified files
- Audit logging of all file operations

AGENT USAGE:
All AI agents use these tools to:
- Read DNA documents (vision, principles, architecture, etc.)
- Create and update specifications and reports  
- Write test results and quality assessments
- Manage project documentation and artifacts
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass

# CrewAI imports
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Project imports
from config.settings import PROJECT_ROOT, DOCS_DIR, DNA_DIR, STATE_DIR

@dataclass
class FileOperation:
    """Record of a file operation for audit logging."""
    timestamp: datetime
    operation: str  # 'read', 'write', 'create', 'delete'
    file_path: str
    agent_name: str
    success: bool
    error_message: Optional[str] = None
    file_size: Optional[int] = None

class FileOperationLogger:
    """
    Centralized logging for all file operations by AI agents.
    
    SECURITY PURPOSE:
    - Track all file access for debugging and security auditing
    - Identify potential issues with agent file operations
    - Monitor resource usage and detect anomalies
    
    🔧 ADAPTATION: Modify logging strategy for your security requirements
    """
    
    def __init__(self):
        self.log_file = STATE_DIR / "logs" / "file_operations.json"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def log_operation(self, operation: FileOperation):
        """Log a file operation to the audit trail."""
        try:
            # Read existing log
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new operation
            logs.append({
                "timestamp": operation.timestamp.isoformat(),
                "operation": operation.operation,
                "file_path": operation.file_path,
                "agent_name": operation.agent_name,
                "success": operation.success,
                "error_message": operation.error_message,
                "file_size": operation.file_size
            })
            
            # Keep only last 1000 operations to prevent unbounded growth
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Write back to log
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Failed to log file operation: {e}")

# Global logger instance
file_logger = FileOperationLogger()

class FilePathValidator:
    """
    Validates file paths to prevent security issues and ensure agents
    only access approved directories and file types.
    
    SECURITY PRINCIPLES:
    - Whitelist approach: Only explicitly allowed paths are accessible
    - No directory traversal: Prevents access outside project boundaries
    - File type restrictions: Only approved extensions allowed
    - Size limits: Prevents resource exhaustion attacks
    
    🔧 ADAPTATION: Update allowed paths and restrictions for your project
    """
    
    # 🔧 ADAPT: Define allowed directories for your project structure
    ALLOWED_READ_PATHS = [
        "docs/",           # Project documentation
        "config/",         # Configuration files
        "templates/",      # Templates and examples
        "specs/",          # Generated specifications (if stored locally)
        "reports/",        # Generated reports and artifacts
    ]
    
    ALLOWED_WRITE_PATHS = [
        "docs/specs/",     # AI-generated specifications
        "reports/",        # AI-generated reports
        "state/",          # Agent state and temporary files
        "monitoring/reports/",  # Quality and performance reports
    ]
    
    # 🔧 ADAPT: Define allowed file extensions for your project needs
    ALLOWED_READ_EXTENSIONS = {
        '.md', '.txt', '.json', '.yml', '.yaml', '.toml', 
        '.py', '.js', '.ts', '.jsx', '.tsx',  # Source code
        '.html', '.css', '.svg',              # Web assets
        '.csv', '.xml'                        # Data files
    }
    
    ALLOWED_WRITE_EXTENSIONS = {
        '.md', '.txt', '.json', '.yml', '.yaml',  # Documentation and config
        '.log', '.csv',                           # Reports and logs
        '.html', '.svg'                           # Generated assets
    }
    
    # 🔧 ADAPT: Adjust size limits based on your expected file sizes
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB limit
    
    @classmethod
    def validate_read_path(cls, file_path: Union[str, Path]) -> tuple[bool, str]:
        """
        Validate that a file path is safe for reading.
        
        Returns:
            (is_valid, error_message)
        """
        return cls._validate_path(file_path, cls.ALLOWED_READ_PATHS, cls.ALLOWED_READ_EXTENSIONS, "read")
    
    @classmethod  
    def validate_write_path(cls, file_path: Union[str, Path]) -> tuple[bool, str]:
        """
        Validate that a file path is safe for writing.
        
        Returns:
            (is_valid, error_message)
        """
        return cls._validate_path(file_path, cls.ALLOWED_WRITE_PATHS, cls.ALLOWED_WRITE_EXTENSIONS, "write")
    
    @classmethod
    def _validate_path(cls, file_path: Union[str, Path], allowed_paths: List[str], 
                      allowed_extensions: set, operation: str) -> tuple[bool, str]:
        """Internal path validation logic."""
        try:
            # Convert to Path object and resolve
            path = Path(file_path).resolve()
            
            # Ensure path is within project boundaries
            try:
                path.relative_to(PROJECT_ROOT.resolve())
            except ValueError:
                return False, f"Path outside project boundaries: {file_path}"
            
            # Check against allowed paths
            relative_path = str(path.relative_to(PROJECT_ROOT))
            path_allowed = any(relative_path.startswith(allowed) for allowed in allowed_paths)
            
            if not path_allowed:
                return False, f"Path not in allowed {operation} directories: {file_path}"
            
            # Check file extension
            if path.suffix.lower() not in allowed_extensions:
                return False, f"File extension not allowed for {operation}: {path.suffix}"
            
            # For write operations, check if parent directory exists or can be created
            if operation == "write":
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # For read operations, check if file exists
            if operation == "read" and not path.exists():
                return False, f"File does not exist: {file_path}"
            
            # Check file size for existing files
            if path.exists() and path.stat().st_size > cls.MAX_FILE_SIZE_BYTES:
                return False, f"File too large (max {cls.MAX_FILE_SIZE_BYTES} bytes): {file_path}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Path validation error: {str(e)}"

class FileReadInput(BaseModel):
    """Input model for file reading operations."""
    file_path: str = Field(..., description="Path to the file to read")
    encoding: str = Field(default="utf-8", description="File encoding (default: utf-8)")
    agent_name: str = Field(default="unknown", description="Name of the agent performing the operation")

class FileWriteInput(BaseModel):
    """Input model for file writing operations."""
    file_path: str = Field(..., description="Path where the file should be saved")
    content: str = Field(..., description="Content to write to the file")
    encoding: str = Field(default="utf-8", description="File encoding (default: utf-8)")
    agent_name: str = Field(default="unknown", description="Name of the agent performing the operation")
    create_backup: bool = Field(default=True, description="Whether to create a backup of existing file")

class FileReadTool(BaseTool):
    """
    Secure file reading tool for AI agents.
    
    CAPABILITIES:
    - Read project DNA documents, specifications, and configuration files
    - Automatic encoding detection and handling
    - Security validation and audit logging
    - Graceful error handling with informative messages
    
    USAGE:
    ```python
    from tools.file_tools import FileReadTool
    
    tool = FileReadTool()
    content = tool._run("docs/dna/vision_and_mission.md", agent_name="projektledare")
    ```
    
    🔧 ADAPTATION: Modify error handling and response format for your needs
    """
    
    name: str = "file_read_tool"
    description: str = """
    Read the contents of a file safely with validation and logging.
    
    Use this tool to:
    - Read project DNA documents (vision, principles, architecture, etc.)
    - Access configuration files and templates
    - Read existing specifications and reports
    - Load any text-based project files
    
    The tool automatically validates file paths for security and logs all operations.
    """
    args_schema: type[BaseModel] = FileReadInput
    
    def _run(self, file_path: str, encoding: str = "utf-8", agent_name: str = "unknown") -> str:
        """
        Read file contents with security validation and logging.
        
        Args:
            file_path: Path to file to read
            encoding: File encoding (default: utf-8)
            agent_name: Name of agent performing operation
            
        Returns:
            File contents as string, or error message if failed
        """
        operation_start = datetime.now()
        
        try:
            # Validate file path
            is_valid, error_msg = FilePathValidator.validate_read_path(file_path)
            if not is_valid:
                file_logger.log_operation(FileOperation(
                    timestamp=operation_start,
                    operation="read",
                    file_path=file_path,
                    agent_name=agent_name,
                    success=False,
                    error_message=f"Path validation failed: {error_msg}"
                ))
                return f"Error: {error_msg}"
            
            # Read file content
            resolved_path = Path(file_path).resolve()
            with open(resolved_path, 'r', encoding=encoding) as file:
                content = file.read()
            
            # Log successful operation
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="read",
                file_path=str(resolved_path),
                agent_name=agent_name,
                success=True,
                file_size=len(content.encode(encoding))
            ))
            
            return content
            
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error reading {file_path} with {encoding}: {str(e)}"
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="read",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            
            # Try alternative encodings
            for alt_encoding in ['utf-8', 'latin-1', 'cp1252']:
                if alt_encoding != encoding:
                    try:
                        with open(resolved_path, 'r', encoding=alt_encoding) as file:
                            content = file.read()
                        return f"# Note: File read with {alt_encoding} encoding instead of {encoding}\n\n{content}"
                    except:
                        continue
            
            return f"Error: Could not read file with any supported encoding: {error_msg}"
            
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="read",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            return f"Error: {error_msg}"
            
        except PermissionError:
            error_msg = f"Permission denied reading: {file_path}"
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="read",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error reading {file_path}: {str(e)}"
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="read",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            return f"Error: {error_msg}"

class FileWriteTool(BaseTool):
    """
    Secure file writing tool for AI agents.
    
    CAPABILITIES:
    - Write specifications, reports, and documentation
    - Automatic backup of existing files
    - Directory creation as needed
    - Security validation and audit logging
    - UTF-8 encoding with BOM handling
    
    USAGE:
    ```python
    from tools.file_tools import FileWriteTool
    
    tool = FileWriteTool()
    result = tool._run(
        file_path="docs/specs/user-auth-spec.md",
        content="# User Authentication Specification\n...",
        agent_name="speldesigner"
    )
    ```
    
    🔧 ADAPTATION: Modify backup strategy and file handling for your workflow
    """
    
    name: str = "file_write_tool"
    description: str = """
    Write content to a file safely with validation, backup, and logging.
    
    Use this tool to:
    - Create and update specifications and documentation
    - Write test reports and quality assessments
    - Generate project artifacts and outputs
    - Save any text-based content
    
    The tool automatically creates backups, validates paths, and logs all operations.
    """
    args_schema: type[BaseModel] = FileWriteInput
    
    def _run(self, file_path: str, content: str, encoding: str = "utf-8", 
             agent_name: str = "unknown", create_backup: bool = True) -> str:
        """
        Write content to file with security validation and logging.
        
        Args:
            file_path: Path where file should be saved
            content: Content to write to file
            encoding: File encoding (default: utf-8)
            agent_name: Name of agent performing operation
            create_backup: Whether to backup existing file
            
        Returns:
            Success message with file info, or error message if failed
        """
        operation_start = datetime.now()
        
        try:
            # Validate file path
            is_valid, error_msg = FilePathValidator.validate_write_path(file_path)
            if not is_valid:
                file_logger.log_operation(FileOperation(
                    timestamp=operation_start,
                    operation="write",
                    file_path=file_path,
                    agent_name=agent_name,
                    success=False,
                    error_message=f"Path validation failed: {error_msg}"
                ))
                return f"Error: {error_msg}"
            
            resolved_path = Path(file_path).resolve()
            
            # Create backup if file exists and backup is requested
            if create_backup and resolved_path.exists():
                backup_path = self._create_backup(resolved_path)
                backup_info = f" (backup created: {backup_path.name})"
            else:
                backup_info = ""
            
            # Ensure parent directory exists
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(resolved_path, 'w', encoding=encoding) as file:
                file.write(content)
            
            # Get file size for logging
            file_size = resolved_path.stat().st_size
            
            # Log successful operation
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="write",
                file_path=str(resolved_path),
                agent_name=agent_name,
                success=True,
                file_size=file_size
            ))
            
            return f"File written successfully: {resolved_path}{backup_info} ({file_size} bytes)"
            
        except PermissionError:
            error_msg = f"Permission denied writing to: {file_path}"
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="write",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            return f"Error: {error_msg}"
            
        except OSError as e:
            error_msg = f"OS error writing {file_path}: {str(e)}"
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="write",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error writing {file_path}: {str(e)}"
            file_logger.log_operation(FileOperation(
                timestamp=operation_start,
                operation="write",
                file_path=file_path,
                agent_name=agent_name,
                success=False,
                error_message=error_msg
            ))
            return f"Error: {error_msg}"
    
    def _create_backup(self, file_path: Path) -> Path:
        """
        Create a timestamped backup of an existing file.
        
        BACKUP STRATEGY:
        - Append timestamp to filename before extension
        - Store in same directory as original file  
        - Format: filename_YYYYMMDD_HHMMSS.ext
        - Automatically clean up old backups (keep last 5)
        
        🔧 ADAPTATION: Modify backup strategy for your needs
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        # Copy original to backup
        shutil.copy2(file_path, backup_path)
        
        # Clean up old backups (keep only last 5)
        self._cleanup_old_backups(file_path)
        
        return backup_path
    
    def _cleanup_old_backups(self, original_file: Path):
        """Remove old backup files, keeping only the 5 most recent."""
        try:
            # Find all backup files for this file
            pattern = f"{original_file.stem}_*{original_file.suffix}"
            backup_files = list(original_file.parent.glob(pattern))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Remove old backups (keep only 5 most recent)
            for old_backup in backup_files[5:]:
                old_backup.unlink()
                
        except Exception as e:
            # Don't fail the main operation if backup cleanup fails
            print(f"Warning: Failed to cleanup old backups: {e}")

# Convenience functions for direct usage
def read_file(file_path: str, agent_name: str = "unknown", encoding: str = "utf-8") -> str:
    """
    Convenience function to read a file directly.
    
    🔧 ADAPTATION: Add any domain-specific file reading logic here
    """
    tool = FileReadTool()
    return tool._run(file_path=file_path, agent_name=agent_name, encoding=encoding)

def write_file(file_path: str, content: str, agent_name: str = "unknown", 
               encoding: str = "utf-8", create_backup: bool = True) -> str:
    """
    Convenience function to write a file directly.
    
    🔧 ADAPTATION: Add any domain-specific file writing logic here
    """
    tool = FileWriteTool()
    return tool._run(
        file_path=file_path, 
        content=content, 
        agent_name=agent_name, 
        encoding=encoding,
        create_backup=create_backup
    )