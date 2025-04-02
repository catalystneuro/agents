import os
import re
import glob
from pathlib import Path
from typing import Optional, List, Dict, Any
from smolagents import Tool

# Configure logging
from utils.logger import set_logger
logger = set_logger(__name__)


class FileSystemTool(Tool):
    """Base class for file system operations tools."""

    def __init__(self, work_dir: str = "/home/agent_workspace"):
        super().__init__()
        self.work_dir = work_dir

    def _validate_path_write(self, path: str) -> str:
        if not path:
            raise ValueError("Path cannot be empty")

        # Convert to absolute path
        abs_path = os.path.abspath(path)

        # Basic path validation
        if not os.path.normpath(abs_path):
            raise ValueError(f"Invalid path: {path}")

        # Validate working directory
        if not abs_path.startswith(self.work_dir):
            raise ValueError(f"Path {abs_path} is outside of the agent working directory {self.work_dir}")

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
    description = "Request to write content to a file at the specified path. If the file exists, it will be overwritten with the provided content. If the file doesn't exist, it will be created. This tool will automatically create any directories needed to write the file."
    inputs = {
        "path": {
            "type": "string",
            "description": "The path of the file to write to (relative to the agent's working directory). This tool will automatically create any necessary directories in the path."
        },
        "content": {
            "type": "string",
            "description": "The content to write to the file. ALWAYS provide the COMPLETE intended content of the file, without any truncation or omissions. You MUST include ALL parts of the file, even if they haven't been modified."
        },
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
            return f"Failed to write to file {path}: {str(e)}"


class ReadFileTool(FileSystemTool):
    name = "read_file"
    description = "Request to read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file you do not know the contents of, for example to analyze code, review text files, or extract information from configuration files."
    inputs = {
        "path": {
            "type": "string",
            "description": "The path of the file to read (relative to the agent's working directory). The file must exist and be readable."
        },
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
            return f"Failed to read file {path}: {str(e)}"


class ReplaceInFileTool(FileSystemTool):
    name = "replace_in_file"
    description = """
    Request to replace sections of content in an existing file. This tool should be used when you
    need to make targeted changes to specific parts of a file without overwriting the entire file.
    It's especially useful for small, localized changes like updating function implementations,
    changing variable names, or modifying specific sections of text.
    """
    inputs = {
        "path": {
            "type": "string",
            "description": "The path of the file to modify (relative to the agent's working directory). The file must exist."
        },
        "search": {
            "type": "string",
            "description": "The exact content to find in the file. This must match character-for-character, including whitespace and indentation."
        },
        "replace": {
            "type": "string",
            "description": "The new content to replace the found content with. To delete content, provide an empty string."
        },
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
            return f"Failed to replace content in file {path}: {str(e)}"


class SearchFilesTool(FileSystemTool):
    name = "search_files"
    description = """
    Request to perform a regex search across files in a specified directory, providing context-rich results.
    This tool searches for patterns or specific content across multiple files, displaying each match with
    encapsulating context. It's particularly useful for understanding code patterns, finding specific
    implementations, or identifying areas that need refactoring.
    """
    inputs = {
        "path": {
            "type": "string",
            "description": "The path of the directory to search in (relative to the agent's working directory). This directory will be recursively searched."
        },
        "regex": {
            "type": "string",
            "description": "The regular expression pattern to search for. Uses standard regex syntax. Craft patterns carefully to balance specificity and flexibility."
        },
        "file_pattern": {
            "type": "string",
            "description": "Optional glob pattern to filter files (e.g., '*.py' for Python files, '*.{js,ts}' for JavaScript and TypeScript). If not provided, it will search all files.",
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
            return f"Failed to search files in {path}: {str(e)}"


class ListFilesTool(FileSystemTool):
    name = "list_files"
    description = """
    Request to list files and directories within the specified directory. This provides an overview
    of the contents at the specified path, which can be useful for navigating and understanding
    the structure of a project or filesystem.
    """
    inputs = {
        "path": {
            "type": "string",
            "description": "The path of the directory to list contents for (relative to the agent's working directory). The directory must exist."
        },
        "recursive": {
            "type": "boolean",
            "description": "Whether to list files recursively. If true, will list all files and directories recursively. If false or not provided, it will only list the top-level contents.",
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
            return f"Failed to list contents of {path}: {str(e)}"


class DeleteFileTool(FileSystemTool):
    name = "delete_file"
    description = "Delete a file from the filesystem"
    inputs = {
        "path": {"type": "string", "description": "Path to the file to delete"},
    }
    output_type = "string"

    def forward(self, path: str) -> str:
        try:
            path = self._validate_path_write(path)

            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")

            if not os.path.isfile(path):
                raise IsADirectoryError(f"Path is not a file: {path}")

            os.remove(path)

            logger.info(f"Successfully deleted file: {path}")
            return f"Successfully deleted file: {path}"

        except Exception as e:
            logger.error(f"Failed to delete file {path}: {str(e)}")
            return f"Failed to delete file {path}: {str(e)}"


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
            logger.error(f"Failed to generate directory tree for {path}: {str(e)}")
            return f"Failed to generate directory tree for {path}: {str(e)}"
