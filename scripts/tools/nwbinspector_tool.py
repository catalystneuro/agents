import os
from pathlib import Path
from smolagents import Tool

# Configure logging
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class NWBInspectorTool(Tool):
    name = "inspect_nwb_files"
    description = """
    Request to inspect and perform quality control checks on NWB (Neurodata Without Borders) files 
    in a directory. This tool examines NWB files for compliance with the NWB standard, identifies
    potential issues, and validates file structure and content integrity.
    """
    inputs = {
        "nwb_dir_path": {
            "type": "string",
            "description": "The path to the directory containing NWB files to be inspected (relative to the agent's working directory). The directory must exist and contain files with the .nwb extension.",
        },
    }
    output_type = "string"

    def _validate_read_dir(self, dir_path: str) -> str:
        # Convert to absolute path
        abs_path = os.path.abspath(dir_path)

        # Basic path validation
        if not os.path.normpath(abs_path):
            raise ValueError(f"Invalid path: {dir_path}")

        # Validate working directory
        allowed_working_dir = os.getenv("AGENT_WORK_DIR", "/home/agent_workspace")
        if not abs_path.startswith(allowed_working_dir):
            raise ValueError(
                f"Path {abs_path} is outside of the agent working directory {allowed_working_dir}"
            )

        return abs_path

    def forward(
        self,
        nwb_dir_path: str,
    ) -> str:
        try:
            from nwbinspector import inspect_nwbfile

            # Validate output directory
            work_dir = self._validate_read_dir(nwb_dir_path)

            results = dict()
            for p in Path(work_dir).glob("*.nwb"):
                results[p.name] = inspect_nwbfile(nwbfile_path=str(p.resolve()))

            return str(results)
        except Exception as e:
            logger.error(f"Failed to inspect NWB files: {str(e)}")
            return f"Failed to inspect NWB files: {str(e)}"
