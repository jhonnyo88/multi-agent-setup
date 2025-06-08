"""
Contextual Tools for AI Agents - FIXED for CrewAI 0.28.8
========================================================

PURPOSE:
Dessa verktyg ger agenterna förmågan att förstå sin egen arbetsmiljö,
t.ex. att söka efter filer och förstå katalogstrukturen.

FIXED FOR CREWAI 0.28.8:
- Compatible tool inheritance
- Proper error handling
- Fallback functionality
"""
from typing import Type, List
import os
from pathlib import Path
from tools.tool_base import UniversalBaseTool as BaseTool


# FIXED: CrewAI 0.28.8 compatible imports
try:
    # Try newer CrewAI versions first
    from crewai.tools import BaseTool
    CREWAI_TOOLS_V2 = True
    print("✅ Using crewai.tools.BaseTool for context tools")
except ImportError:
    try:
        # Try crewai_tools package
        from crewai_tools import BaseTool
        CREWAI_TOOLS_V2 = True
        print("✅ Using crewai_tools.BaseTool for context tools")
    except ImportError:
        try:
            # Fallback to LangChain
            from langchain.tools import BaseTool
            CREWAI_TOOLS_V2 = False
            print("⚠️  Using LangChain BaseTool fallback for context tools")
        except ImportError:
            # Manual implementation as last resort
            print("❌ No BaseTool found for context tools, using manual implementation")
            from pydantic import BaseModel
            
            class BaseTool(BaseModel):
                """Manual BaseTool implementation for CrewAI 0.28.8"""
                name: str
                description: str
                
                def _run(self, *args, **kwargs):
                    raise NotImplementedError("Subclasses must implement _run method")
                
                def run(self, *args, **kwargs):
                    """Run method that CrewAI expects"""
                    return self._run(*args, **kwargs)
            
            CREWAI_TOOLS_V2 = False

from pydantic import BaseModel, Field
from config.settings import PROJECT_ROOT

class SearchInput(BaseModel):
    """Input för FileSearchTool."""
    query: str = Field(..., description="Filnamnet eller söktermen att leta efter.")

class FileSearchTool(BaseTool):
    """
    Tool for searching files within the project structure.
    
    FIXED FOR CREWAI 0.28.8:
    - Compatible tool inheritance
    - Proper error handling
    - Support for both _run and run methods
    """
    name: str = "File Search Tool"
    description: str = (
        "Search for files within the project directory by filename or content. "
        "Perfect when you know what a file is called but not where it's located. "
        "Provide a search query (filename or part of filename) as input."
    )

    def _run(self, query: str) -> str:
        """
        FIXED: Search through the project and return matching file paths.
        Works with CrewAI 0.28.8
        """
        try:
            results = []
            # Normalize query for handling both filename and general searches
            normalized_query = query.lower().strip()
            
            # Search through project directory
            for root, dirs, files in os.walk(str(PROJECT_ROOT)):
                # Skip certain directories to reduce noise
                if any(skip_dir in root for skip_dir in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                    continue
                
                for name in files:
                    if normalized_query in name.lower():
                        full_path = Path(root) / name
                        # Ensure path is relative to project root
                        try:
                            relative_path = full_path.relative_to(PROJECT_ROOT)
                            results.append(str(relative_path).replace('\\', '/'))  # Consistent with forward slash
                        except ValueError:
                            # Ignore files outside project root
                            continue
            
            if not results:
                return f"No files matching '{query}' found in the project."
            
            return f"Found following matching files:\n" + "\n".join(results)
        
        except Exception as e:
            return f"Error searching for files: {str(e)}"

    # FIXED: For CrewAI 0.28.8 compatibility
    def run(self, query: str) -> str:
        """Public run method that CrewAI 0.28.8 expects"""
        return self._run(query)


class DirectoryListTool(BaseTool):
    """
    Tool for listing contents of a specific directory.
    
    FIXED FOR CREWAI 0.28.8:
    - Compatible tool inheritance
    - Proper error handling
    - Support for both _run and run methods
    """
    name: str = "Directory List Tool"
    description: str = (
        "List the contents of a specific directory within the project. "
        "Provide a directory path relative to project root."
    )

    def _run(self, directory_path: str) -> str:
        """
        FIXED: List contents of specified directory.
        Works with CrewAI 0.28.8
        """
        try:
            # Convert to absolute path
            if not Path(directory_path).is_absolute():
                full_path = PROJECT_ROOT / directory_path
            else:
                full_path = Path(directory_path)
            
            if not full_path.exists():
                return f"Directory does not exist: {directory_path}"
            
            if not full_path.is_dir():
                return f"Path is not a directory: {directory_path}"
            
            # List contents
            contents = []
            for item in full_path.iterdir():
                if item.is_dir():
                    contents.append(f"📁 {item.name}/")
                else:
                    # Show file size for files
                    try:
                        size = item.stat().st_size
                        if size < 1024:
                            size_str = f"{size}B"
                        elif size < 1024 * 1024:
                            size_str = f"{size // 1024}KB"
                        else:
                            size_str = f"{size // (1024 * 1024)}MB"
                        contents.append(f"📄 {item.name} ({size_str})")
                    except:
                        contents.append(f"📄 {item.name}")
            
            if not contents:
                return f"Directory is empty: {directory_path}"
            
            result = f"Contents of {directory_path}:\n"
            result += "\n".join(sorted(contents))
            return result
        
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    # FIXED: For CrewAI 0.28.8 compatibility  
    def run(self, directory_path: str) -> str:
        """Public run method that CrewAI 0.28.8 expects"""
        return self._run(directory_path)


class ProjectStructureTool(BaseTool):
    """
    Tool for getting overview of project structure.
    
    FIXED FOR CREWAI 0.28.8:
    - Compatible tool inheritance
    - Proper error handling
    - Support for both _run and run methods
    """
    name: str = "Project Structure Tool"
    description: str = (
        "Get an overview of the entire project structure showing main directories "
        "and important files. No parameters needed."
    )

    def _run(self, max_depth: int = 3) -> str:
        """
        FIXED: Generate project structure overview.
        Works with CrewAI 0.28.8
        """
        try:
            structure_lines = []
            
            def add_directory_tree(path: Path, prefix: str = "", current_depth: int = 0):
                """Recursively build directory tree"""
                if current_depth >= max_depth:
                    return
                
                try:
                    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                    
                    for i, item in enumerate(items):
                        # Skip hidden and cache directories
                        if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', 'venv']:
                            continue
                        
                        is_last = i == len(items) - 1
                        current_prefix = "└── " if is_last else "├── "
                        
                        if item.is_dir():
                            structure_lines.append(f"{prefix}{current_prefix}📁 {item.name}/")
                            # Recurse into subdirectory
                            next_prefix = prefix + ("    " if is_last else "│   ")
                            add_directory_tree(item, next_prefix, current_depth + 1)
                        else:
                            # Show important files
                            if item.suffix in ['.py', '.md', '.json', '.yml', '.yaml', '.toml']:
                                structure_lines.append(f"{prefix}{current_prefix}📄 {item.name}")
                
                except PermissionError:
                    structure_lines.append(f"{prefix}❌ Permission denied")
                except Exception as e:
                    structure_lines.append(f"{prefix}⚠️ Error: {str(e)}")
            
            structure_lines.append(f"📁 {PROJECT_ROOT.name}/ (Project Root)")
            add_directory_tree(PROJECT_ROOT)
            
            return "\n".join(structure_lines)
        
        except Exception as e:
            return f"Error generating project structure: {str(e)}"

    # FIXED: For CrewAI 0.28.8 compatibility
    def run(self, max_depth: int = 3) -> str:
        """Public run method that CrewAI 0.28.8 expects"""
        return self._run(max_depth)


# Convenience function for testing all context tools
def test_context_tools():
    """Test all context tools"""
    print("🧪 Testing Context Tools...")
    
    try:
        # Test File Search Tool
        print("\n🔍 Testing File Search Tool...")
        search_tool = FileSearchTool()
        search_result = search_tool.run("settings.py")
        print("✅ File search completed")
        print(f"Result preview: {search_result[:100]}...")
        
        # Test Directory List Tool
        print("\n📁 Testing Directory List Tool...")
        dir_tool = DirectoryListTool()
        dir_result = dir_tool.run("agents")
        print("✅ Directory listing completed")
        print(f"Result preview: {dir_result[:100]}...")
        
        # Test Project Structure Tool
        print("\n🏗️ Testing Project Structure Tool...")
        structure_tool = ProjectStructureTool()
        structure_result = structure_tool.run(2)  # Depth 2
        print("✅ Project structure generated")
        print(f"Result preview: {structure_result[:200]}...")
        
        print("\n🎉 All context tools tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Context tools test failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests when module is executed directly
    test_context_tools()