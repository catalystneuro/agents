import os
import asyncio
from smolagents import Tool

from .semantic_search import search

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Check environment variables
if not os.getenv("OPENROUTER_API_KEY", None):
    logger.error("OPENROUTER_API_KEY environment variable is not set")
    raise ValueError("Please set the OPENROUTER_API_KEY environment variable.")

if not os.getenv("OPENAI_API_KEY", None):
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

if not os.getenv("QDRANT_API_KEY", None):
    logger.error("QDRANT_API_KEY environment variable is not set")
    raise ValueError("Please set the QDRANT_API_KEY environment variable.")



class NeuroconvSpecialistTool(Tool):
    name = "neuroconv_specialist_tool"
    description = """
    Use this tool to ask questions and learn about NeuroConv.
    NeuroConv is a Python package for converting neurophysiology data in a variety of proprietary formats to the Neurodata Without Borders (NWB) standard.
    Features:
    - Reads data from 40 popular neurophysiology data formats and writes to NWB using best practices.
    - Extracts relevant metadata from each format.
    - Handles large data volume by reading datasets piece-wise.
    - Minimizes the size of the NWB files by automatically applying chunking and lossless compression.
    - Supports ensembles of multiple data streams, and supports common methods for temporal alignment of streams.

    How to use the Neuroconv specialist: Formulate a concise search query and provide the relevant context.
    Example:
    query = "Convert spiking data from Blackrock systems to NWB."
    context = "User wants to convert its recorded data to the NWB format, using NeuroConv."
    """
    inputs = {
        "query": {
            "type": "string",
            "description": "A concise search query, containing the keywords of interest.",
        },
        "context": {
            "type": "string",
            "description": "A short but relevant context for the query.",
        },
    }
    output_type = "string"

    def forward(
        self,
        query: str,
        context: str,
    ):
        result = asyncio.run(
            search(
                query=query,
                context=context,
                qdrant_url="https://f068e67a-2d2b-45b8-8098-f6c354d763ec.europe-west3-0.gcp.cloud.qdrant.io:6333",
                collection_name="neuroconv",
                keywords=None,
                qdrant_api_key=os.getenv("QDRANT_API_KEY"),
                timeout=60.0,
                return_digest_summary=True,
                return_references=True,
                limit=10,
                model="openrouter/openai/o3-mini",
            )
        )
        return str(result)


neuroconv_specialist_tool = NeuroconvSpecialistTool()
