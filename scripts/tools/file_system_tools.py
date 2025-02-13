import os
import re
import glob
from pathlib import Path
from typing import Optional, List, Dict, Any
from smolagents import Tool

# Configure logging
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class FileSystemTool(Tool):
    """Base class for file system operations tools."""

    def _validate_path_write(self, path: str) -> str:
        if not path:
            raise ValueError("Path cannot be empty")

        # Convert to absolute path
        abs_path = os.path.abspath(path)

        # Basic path validation
        if not os.path.normpath(abs_path):
            raise ValueError(f"Invalid path: {path}")

        # Validate working directory
        work_dir = os.getenv("AGENT_WORK_DIR", "/home/agent_workspace")
        if not abs_path.startswith(work_dir):
            raise ValueError(f"Path {abs_path} is outside of the agent working directory {work_dir}")

        return abs_path

    def _validate_path_read(self, path: str) -> str:
        if not path:
            raise ValueError("Path cannot be empty")

        # Convert to absolute path
        abs_path = os.path.abspath(path)

        # Basic path validation
        if not os.path.normpath(abs_path):
            raise ValueError(f"Invalid path: {path}")

        return abs_path


class WriteToFileTool(FileSystemTool):
    name = "write_to_file"
    description = "Create or overwrite files with specified content"
    inputs = {
        "path": {"type": "string", "description": "Path to the file to write to"},
        "content": {"type": "string", "description": "Content to write to the file"},
    }
    output_type = "string"

    def forward(self, path: str, content: str) -> str:
        try:
            path = self._validate_path_write(path)

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Successfully wrote to file: {path}")
            return f"Successfully wrote content to {path}"

        except Exception as e:
            logger.error(f"Failed to write to file {path}: {str(e)}")
            raise


class ReadFileTool(FileSystemTool):
    name = "read_file"
    description = "Read contents of a file"
    inputs = {
        "path": {"type": "string", "description": "Path to the file to read"},
    }
    output_type = "string"

    def forward(self, path: str) -> str:
        try:
            path = self._validate_path_read(path)

            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(f"Successfully read file: {path}")
            return content

        except Exception as e:
            logger.error(f"Failed to read file {path}: {str(e)}")
            raise


class ReplaceInFileTool(FileSystemTool):
    name = "replace_in_file"
    description = "Make targeted edits to specific parts of a file"
    inputs = {
        "path": {"type": "string", "description": "Path to the file to modify"},
        "search": {"type": "string", "description": "Content to find in the file"},
        "replace": {"type": "string", "description": "Content to replace with"},
    }
    output_type = "string"

    def forward(self, path: str, search: str, replace: str) -> str:
        try:
            path = self._validate_path_write(path)

            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")

            # Read file content
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Perform replacement
            new_content = content.replace(search, replace)

            # Write back to file
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(f"Successfully replaced content in file: {path}")
            return f"Successfully replaced content in {path}"

        except Exception as e:
            logger.error(f"Failed to replace content in file {path}: {str(e)}")
            raise


class SearchFilesTool(FileSystemTool):
    name = "search_files"
    description = "Search files using regex patterns"
    inputs = {
        "path": {"type": "string", "description": "Directory to search in"},
        "regex": {"type": "string", "description": "Regular expression pattern to search for"},
        "file_pattern": {
            "type": "string",
            "description": "Optional glob pattern to filter files",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, path: str, regex: str, file_pattern: Optional[str] = None) -> str:
        try:
            path = self._validate_path_read(path)

            if not os.path.isdir(path):
                raise NotADirectoryError(f"Not a directory: {path}")

            # Compile regex pattern
            pattern = re.compile(regex)

            # Get list of files to search
            if file_pattern:
                files = glob.glob(os.path.join(path, "**", file_pattern), recursive=True)
            else:
                files = glob.glob(os.path.join(path, "**", "*"), recursive=True)

            # Search files
            results = []
            for file in files:
                if os.path.isfile(file):
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            content = f.read()
                            matches = pattern.finditer(content)
                            for match in matches:
                                start = max(0, match.start() - 50)
                                end = min(len(content), match.end() + 50)
                                context = content[start:end]
                                results.append(
                                    f"File: {file}\nMatch: {match.group()}\nContext: ...{context}..."
                                )
                    except Exception as e:
                        logger.warning(f"Failed to search file {file}: {str(e)}")

            logger.info(f"Successfully searched files in: {path}")
            return "\n\n".join(results) if results else "No matches found"

        except Exception as e:
            logger.error(f"Failed to search files in {path}: {str(e)}")
            raise


class ListFilesTool(FileSystemTool):
    name = "list_files"
    description = "List directory contents"
    inputs = {
        "path": {"type": "string", "description": "Directory to list contents for"},
        "recursive": {
            "type": "boolean",
            "description": "Whether to list files recursively",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, path: str, recursive: Optional[bool] = False) -> str:
        try:
            path = self._validate_path_read(path)

            if not os.path.isdir(path):
                raise NotADirectoryError(f"Not a directory: {path}")

            # Get file listing
            if recursive:
                files = []
                for root, dirs, filenames in os.walk(path):
                    rel_root = os.path.relpath(root, path)
                    if rel_root == ".":
                        files.extend(filenames)
                    else:
                        files.extend(os.path.join(rel_root, f) for f in filenames)
            else:
                files = os.listdir(path)

            # Sort files
            files.sort()

            logger.info(f"Successfully listed contents of: {path}")
            return "\n".join(files)

        except Exception as e:
            logger.error(f"Failed to list contents of {path}: {str(e)}")
            raise


class DirectoryTreeTool(FileSystemTool):
    name = "directory_tree"
    description = "Generate a tree view of the directory structure"
    inputs = {
        "path": {"type": "string", "description": "Path to the directory to generate tree for"},
    }
    output_type = "string"

    def forward(self, path: str) -> str:
        try:
            from directory_tree import DisplayTree

            path = self._validate_path_read(path)

            tree = DisplayTree(
                dirPath=path,
                stringRep=True,
                header=False,
                maxDepth=float('inf'),
                showHidden=True,
                ignoreList=None,
                onlyFiles=False,
                onlyDirs=False,
                sortBy=0,
            )

            logger.info(f"Directory tree: {tree}")
            return tree

        except Exception as e:
            logger.error(f"Failed to write to file {path}: {str(e)}")
            raise
