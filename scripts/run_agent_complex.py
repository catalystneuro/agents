import os
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    LiteLLMModel,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    PythonInterpreterTool,
    GradioUI,
)
from tools.neuroconv_specialist_tool import NeuroconvSpecialistTool

# Telemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

endpoint = "http://0.0.0.0:6006/v1/traces"
trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))

SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)


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

logger.info("Initializing models and tools...")

# Models
model_search = LiteLLMModel("openrouter/anthropic/claude-3.5-sonnet")
model_manager = LiteLLMModel("openrouter/google/gemini-2.0-flash-001")

# Agents
neuroconv_agent = ToolCallingAgent(
    name="neuroconv_specialist_agent",
    description="""
This is an agent that can perform specialized semantic search about Neuroconv.
Call this agent any time you need to fetch updated information about Neuroconv.
""",
    tools=[
        # DuckDuckGoSearchTool(),
        # VisitWebpageTool(),
        NeuroconvSpecialistTool(),
    ],
    model=model_search,
    # add_base_tools=True,
)

manager_agent = CodeAgent(
    tools=[PythonInterpreterTool()],
    model=model_manager,
    managed_agents=[neuroconv_agent],
    planning_interval=3,
    add_base_tools=False,
)

try:
    logger.info("Starting Gradio interface...")
    # Configure Gradio to be accessible from outside the container
    GradioUI(manager_agent).launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860        # Match the exposed port
    )
except Exception as e:
    logger.error(f"Failed to start Gradio interface: {str(e)}")
    raise
