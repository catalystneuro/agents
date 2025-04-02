import os
import subprocess
from typing import Optional, List, Dict, Any
from smolagents import Tool

# Configure logging
from utils.logger import set_logger
logger = set_logger(__name__)


class ExecuteCommandInTerminalTool(Tool):
    name = "execute_command_in_terminal"
    description = """
    Request to execute a CLI command on the system. Use this when you need to perform system operations
    or run specific commands to accomplish any step in a task. You must tailor your command to the
    system and provide a clear explanation of what the command does. For command chaining, use the
    appropriate chaining syntax for the user's shell. Prefer to execute complex CLI commands over
    creating executable scripts, as they are more flexible and easier to run.
    """
    inputs = {
        "command": {
            "type": "string",
            "description": "The CLI command to execute. This should be valid for the current operating system. Ensure the command is properly formatted and does not contain any harmful instructions.",
        },
        "requires_approval": {
            "type": "boolean",
            "description": "Whether this command requires explicit approval before execution. Set to 'true' for potentially impactful operations like installing/uninstalling packages, deleting/overwriting files, system configuration changes, network operations, or commands with side effects. Set to 'false' for safe operations like reading files/directories, running development servers, building projects, etc.",
        },
        "working_dir": {
            "type": "string",
            "description": "The directory where the command should be executed. If not provided, the command will be executed in the agent's working directory.",
            "nullable": True,
        },
    }
    output_type = "string"

    # Commands that are considered potentially dangerous
    DANGEROUS_COMMANDS = [
        # "rm -rf",
        # "mkfs",
        # "dd",
        # ">",
        # "sudo",
        # "su",
        # "chmod",
        # "chown",
    ]

    def __init__(self, allowed_dirs: List[str] = ["/home/agent_workspace"]):
        super().__init__()
        self.allowed_dirs = allowed_dirs

    def _validate_command(self, command: str) -> None:
        # Check for dangerous commands
        command_lower = command.lower()
        for dangerous_cmd in self.DANGEROUS_COMMANDS:
            if dangerous_cmd in command_lower:
                raise ValueError(
                    f"Command contains potentially dangerous operation: {dangerous_cmd}"
                )

    def _validate_working_dir(self, working_dir: Optional[str]) -> str:
        if working_dir is None:
            raise ValueError("Working directory cannot be empty")

        # Convert to absolute path
        abs_path = os.path.abspath(working_dir)

        # Basic path validation
        if not os.path.normpath(abs_path):
            raise ValueError(f"Invalid path: {working_dir}")

        # Check if directory exists
        if not os.path.isdir(abs_path):
            raise NotADirectoryError(f"Not a directory: {abs_path}")

        # Validate working directory
        if not any(abs_path.startswith(allowed_dir) for allowed_dir in self.allowed_dirs):
            raise ValueError(
                f"Path {abs_path} is outside of the agent allowed directories: {self.allowed_dirs}"
            )

        return abs_path

    def forward(
        self,
        command: str,
        requires_approval: bool,
        working_dir: Optional[str] = None,
    ) -> str:
        try:
            # Validate command
            self._validate_command(command)

            # Validate working directory
            work_dir = self._validate_working_dir(working_dir)

            # Log command execution
            logger.info(f"Executing command: {command}")
            logger.info(f"Working directory: {work_dir}")
            logger.info(f"Requires approval: {requires_approval}")

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True,
            )

            # Format output
            output = []
            if result.stdout:
                output.append("STDOUT:")
                output.append(result.stdout)
            if result.stderr:
                output.append("STDERR:")
                output.append(result.stderr)

            formatted_output = "\n".join(output) if output else "Command completed successfully"
            logger.info("Command execution successful")
            return formatted_output

        except subprocess.CalledProcessError as e:
            error_msg = f"execute_command failed with exit code {e.returncode}"
            if e.stdout:
                error_msg += f"\nSTDOUT:\n{e.stdout}"
            if e.stderr:
                error_msg += f"\nSTDERR:\n{e.stderr}"
            logger.error(error_msg)
            return error_msg

        except Exception as e:
            logger.error(f"Failed to execute command: {str(e)}")
            return f"execute_command failed to execute command: {str(e)}"
