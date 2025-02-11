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


agent = CodeAgent(
    tools=[NeuroconvSpecialistTool()],
    model=LiteLLMModel("openrouter/anthropic/claude-3.5-sonnet"),
    add_base_tools=True,
)

try:
    logger.info("Starting Gradio interface...")
    # Configure Gradio to be accessible from outside the container
    GradioUI(agent).launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860        # Match the exposed port
    )
except Exception as e:
    logger.error(f"Failed to start Gradio interface: {str(e)}")
    raise
