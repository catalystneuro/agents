import os
from typing import Optional
from cookiecutter.main import cookiecutter
from smolagents import Tool

# Configure logging
from utils.logger import set_logger
logger = set_logger(__name__)


class CreateNWBRepoTool(Tool):
    name = "create_nwb_repo"
    description = """
    Request to create a new NWB (Neurodata Without Borders) conversion repository from a template.
    This tool generates a standardized project structure for converting neurophysiology data to the NWB format,
    following best practices and conventions. It uses a cookiecutter template to scaffold the entire project.
    """
    inputs = {
        "lab_name": {
            "type": "string",
            "description": "The name of the research lab or group (e.g., 'Tauffer Lab'). This will be used in naming the repository and in documentation.",
        },
        "conversion_name": {
            "type": "string",
            "description": "A descriptive name for this specific conversion effort (e.g., 'electrophysiology2023a'). This helps identify the specific data modality and experiment being converted.",
        },
        "output_dir": {
            "type": "string",
            "description": "The directory where the repository will be created (relative to the agent's working directory). If the directory doesn't exist, it will be created.",
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
            repo_name = f"{lab_name.lower().replace(' ', '-')}-lab-to-nwb"
            repo_path = os.path.join(work_dir, repo_name)

            logger.info(f"Successfully created repository at: {repo_path}")
            return f"Project created at: {repo_path}"

        except Exception as e:
            logger.error(f"Failed to create repository: {str(e)}")
            return f"Failed to create repository: {str(e)}"
