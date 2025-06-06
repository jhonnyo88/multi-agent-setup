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

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, AliasChoices

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
        # Denna funktion är avsiktligt förenklad för detta exempel.
        # I en fullständig implementation skulle den skriva till logfilen.
        pass

file_logger = FileOperationLogger()

class FilePathValidator:
    """Validates file paths to prevent security issues."""
    ALLOWED_READ_PATHS = ["docs/", "config/", "templates/", "reports/"]
    ALLOWED_WRITE_PATHS = ["reports/", "state/", "docs/specs/", "backend/", "src/"]
    ALLOWED_READ_EXTENSIONS = {'.md', '.txt', '.json', '.yml', '.yaml', '.toml', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.svg', '.csv', '.xml'}
    ALLOWED_WRITE_EXTENSIONS = {'.md', '.txt', '.json', '.yml', '.yaml', '.log', '.csv', '.html', '.svg', '.py', '.tsx'}
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

    @classmethod
    def _validate_path(cls, file_path: Union[str, Path], allowed_paths: List[str], extensions: set, op: str) -> tuple[bool, str]:
        try:
            p = Path(file_path).resolve()
            p.relative_to(PROJECT_ROOT.resolve())
            relative_path_str = str(p.relative_to(PROJECT_ROOT)).replace('\\', '/')
            if not any(relative_path_str.startswith(allowed) for allowed in allowed_paths):
                return False, f"Path not in allowed {op} directories: {file_path}"
            if p.suffix.lower() not in extensions:
                return False, f"File extension not allowed for {op}: {p.suffix}"
            if op == "write":
                p.parent.mkdir(parents=True, exist_ok=True)
            if op == "read" and not p.exists():
                return False, f"File does not exist: {file_path}"
            if p.exists() and p.stat().st_size > cls.MAX_FILE_SIZE_BYTES:
                return False, f"File too large: {file_path}"
            return True, ""
        except Exception as e:
            return False, f"Path validation error: {e}"

    @classmethod
    def validate_read_path(cls, fp: Union[str, Path]) -> tuple[bool, str]:
        return cls._validate_path(fp, cls.ALLOWED_READ_PATHS, cls.ALLOWED_READ_EXTENSIONS, "read")
    
    @classmethod
    def validate_write_path(cls, fp: Union[str, Path]) -> tuple[bool, str]:
        return cls._validate_path(fp, cls.ALLOWED_WRITE_PATHS, cls.ALLOWED_WRITE_EXTENSIONS, "write")

class FileReadInput(BaseModel):
    file_path: str = Field(..., description="Path to the file to read", validation_alias=AliasChoices('file_path', 'path', 'filename'))
    agent_name: str = Field(default="unknown", description="Agent name")

class FileWriteInput(BaseModel):
    file_path: str = Field(..., description="Path to save the file", validation_alias=AliasChoices('file_path', 'filename', 'filepath', 'path'))
    content: str = Field(..., description="Content to write")
    agent_name: str = Field(default="unknown", description="Agent name")

class FileReadTool(BaseTool):
    name: str = "file_read_tool"
    description: str = "Read the contents of a file safely."
    args_schema: type[BaseModel] = FileReadInput
    
    def _run(self, **kwargs) -> str:
        # Använder hjälpfunktionen för att hålla koden ren
        return read_file(**kwargs)

class FileWriteTool(BaseTool):
    name: str = "file_write_tool"
    description: str = "Write content to a file safely."
    args_schema: type[BaseModel] = FileWriteInput
    
    def _run(self, **kwargs) -> str:
        # Använder hjälpfunktionen
        return write_file(**kwargs)

def read_file(file_path: str, agent_name: str = "unknown", encoding: str = "utf-8") -> str:
    """Convenience function to read a file directly."""
    is_valid, error_msg = FilePathValidator.validate_read_path(file_path)
    if not is_valid:
        return f"Error: {error_msg}"
    try:
        with open(Path(file_path).resolve(), 'r', encoding=encoding) as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path: str, content: str, agent_name: str = "unknown", encoding: str = "utf-8", create_backup: bool = True) -> str:
    """Convenience function to write a file directly."""
    is_valid, error_msg = FilePathValidator.validate_write_path(file_path)
    if not is_valid:
        return f"Error: {error_msg}"
    try:
        resolved_path = Path(file_path).resolve()
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        if create_backup and resolved_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = resolved_path.parent / f"{resolved_path.stem}_{timestamp}{resolved_path.suffix}"
            shutil.copy2(resolved_path, backup_path)
        with open(resolved_path, 'w', encoding=encoding) as file:
            file.write(content)
        return f"File written successfully to {resolved_path}"
    except Exception as e:
        return f"Error writing file: {e}"