import os
from typing import Optional
from cookiecutter.main import cookiecutter
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
            extra_context = {
                "lab": lab_name,
                "conversion_name": conversion_name,
            }

            # Generate the project
            cookiecutter(
                self.TEMPLATE_URL,
                extra_context=extra_context,
                no_input=True,
                output_dir=work_dir,
            )

            # Log creation attempt
            logger.info(f"Creating NWB conversion repository:")
            logger.info(f"Template URL: {self.TEMPLATE_URL}")
            logger.info(f"Lab name: {lab_name}")
            logger.info(f"Conversion name: {conversion_name}")
            logger.info(f"Output directory: {work_dir}")

            # Get repository path
            repo_name = f"{lab_name.lower().replace(' ', '-')}-to-nwb"
            repo_path = os.path.join(work_dir, repo_name)

            logger.info(f"Successfully created repository at: {repo_path}")
            return f"Project created at: {repo_path}"

        except Exception as e:
            logger.error(f"Failed to create repository: {str(e)}")
            return f"Failed to create repository: {str(e)}"
