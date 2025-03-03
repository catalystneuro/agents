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
    Request to use the NeuroConv specialist tool to get information about converting neurophysiology data to NWB format.
    
    NeuroConv is a Python package for converting neurophysiology data in a variety of proprietary formats to the 
    Neurodata Without Borders (NWB) standard. This tool provides specialized knowledge about NeuroConv capabilities,
    usage patterns, best practices, and technical details.
    
    Features of NeuroConv:
    - Reads data from 40+ popular neurophysiology data formats and writes to NWB using best practices
    - Extracts relevant metadata from each format
    - Handles large data volume by reading datasets piece-wise
    - Minimizes the size of the NWB files by automatically applying chunking and lossless compression
    - Supports ensembles of multiple data streams and methods for temporal alignment of streams
    
    This tool uses semantic search to find relevant information about NeuroConv based on your query and context.
    """
    inputs = {
        "query": {
            "type": "string",
            "description": "A concise search query about NeuroConv, containing specific keywords related to the information needed (e.g., 'Convert spiking data from Blackrock systems to NWB')."
        },
        "context": {
            "type": "string",
            "description": "Additional context about your question or use case that will help the tool provide more relevant information (e.g., 'I need to convert recorded electrophysiology data to NWB format using NeuroConv')."
        },
    }
    output_type = "string"

    def __init__(
        self,
        return_digest_summary: bool = True,
        llm_model: str = "openrouter/openai/o3-mini",
    ):
        super().__init__()
        self.return_digest_summary = return_digest_summary
        self.llm_model = llm_model

    def forward(
        self,
        query: str,
        context: str,
    ):
        try:
            result = asyncio.run(
                search(
                    query=query,
                    context=context,
                    qdrant_url="https://f068e67a-2d2b-45b8-8098-f6c354d763ec.europe-west3-0.gcp.cloud.qdrant.io:6333",
                    collection_name="neuroconv",
                    keywords=None,
                    qdrant_api_key=os.getenv("QDRANT_API_KEY"),
                    timeout=60.0,
                    return_digest_summary=self.return_digest_summary,
                    return_references=True,
                    limit=10,
                    model=self.llm_model,
                )
            )
            return str(result)
        except Exception as e:
            logger.error(f"neuroconv_specialist_tool failed with error: {str(e)}")
            return f"neuroconv_specialist_tool failed with error: {str(e)}"
