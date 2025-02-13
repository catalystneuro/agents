import os
import subprocess
from typing import Optional
from smolagents import Tool

# Configure logging
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CreateNWBRepoTool(Tool):
    name = "create_nwb_repo"
    description = "Create a new NWB conversion repository from template."
    inputs = {
        "lab_name": {
            "type": "string",
            "description": "Lab name (e.g., 'Tauffer Lab')",
        },
        "conversion_name": {
            "type": "string",
            "description": "Name of the conversion (e.g., 'conversionname2002a')",
        },
        "output_dir": {
            "type": "string",
            "description": "Directory where the repository will be created",
        },
    }
    output_type = "string"

    TEMPLATE_URL = "https://github.com/catalystneuro/cookiecutter-my-lab-to-nwb-template"

    def _validate_output_dir(self, output_dir: str) -> str:
        # Convert to absolute path
        abs_path = os.path.abspath(output_dir)

        # Basic path validation
        if not os.path.normpath(abs_path):
            raise ValueError(f"Invalid path: {output_dir}")

        # Validate working directory
        allowed_working_dir = os.getenv("AGENT_WORK_DIR", "/home/agent_workspace")
        if not abs_path.startswith(allowed_working_dir):
            raise ValueError(
                f"Path {abs_path} is outside of the agent working directory {allowed_working_dir}"
            )

        # Create directory if it doesn't exist
        os.makedirs(abs_path, exist_ok=True)

        return abs_path

    def forward(
        self,
        lab_name: str,
        conversion_name: str,
        output_dir: str,
    ) -> str:
        try:
            # Validate output directory
            work_dir = self._validate_output_dir(output_dir)

            # Prepare cookiecutter context
            context = {
                "lab": lab_name,
                "conversion_name": conversion_name,
            }

            # Create context file
            context_path = os.path.join(work_dir, "cookiecutter.json")
            with open(context_path, "w") as f:
                import json
                json.dump(context, f)

            # Log creation attempt
            logger.info(f"Creating NWB conversion repository:")
            logger.info(f"Template URL: {self.TEMPLATE_URL}")
            logger.info(f"Lab name: {lab_name}")
            logger.info(f"Conversion name: {conversion_name}")
            logger.info(f"Output directory: {work_dir}")

            # Run cookiecutter
            cmd = [
                "cookiecutter",
                "--no-input",
                "--output-dir", work_dir,
                "--config-file", context_path,
                self.TEMPLATE_URL,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            # Clean up context file
            os.remove(context_path)

            # Format output
            output = []
            if result.stdout:
                output.append("STDOUT:")
                output.append(result.stdout)
            if result.stderr:
                output.append("STDERR:")
                output.append(result.stderr)

            # Get repository path
            repo_name = f"{lab_name.lower().replace(' ', '-')}-to-nwb"
            repo_path = os.path.join(work_dir, repo_name)

            formatted_output = "\n".join(output) if output else "Repository created successfully"
            logger.info(f"Successfully created repository at: {repo_path}")
            return f"{formatted_output}\nRepository created at: {repo_path}"

        except subprocess.CalledProcessError as e:
            error_msg = f"Repository creation failed with exit code {e.returncode}"
            if e.stdout:
                error_msg += f"\nSTDOUT:\n{e.stdout}"
            if e.stderr:
                error_msg += f"\nSTDERR:\n{e.stderr}"
            logger.error(error_msg)
            raise

        except Exception as e:
            logger.error(f"Failed to create repository: {str(e)}")
            raise
