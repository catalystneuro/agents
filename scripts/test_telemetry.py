from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel
import os
import base64
from typing import Literal
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from openinference.instrumentation.smolagents import SmolagentsInstrumentor


def set_langfuse():
    LANGFUSE_PUBLIC_KEY = "pk-lf-1e16e3e2-e3e5-4f3e-951c-ef3ceaa8cfa4"
    LANGFUSE_SECRET_KEY = "sk-lf-9be515a8-0aeb-4fa8-aa94-faf4cca28785"
    os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
    os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
    os.environ["LANGFUSE_HOST"] = "http://localhost:3000"

    LANGFUSE_AUTH = base64.b64encode(
        f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()
    ).decode()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.environ.get("LANGFUSE_HOST") + "/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"


def set_telemetry(system: Literal["langfuse", "phoenix"] = "langfuse"):
    if system == "langfuse":
        set_langfuse()
        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        print(f"Using Langfuse telemetry endpoint: {endpoint}")
    else:
        endpoint = "http://0.0.0.0:6006/v1/traces"

    # Create a TracerProvider for OpenTelemetry
    trace_provider = TracerProvider()

    # Add a SimpleSpanProcessor with the OTLPSpanExporter to send traces
    trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

    # Set the global default tracer provider
    trace.set_tracer_provider(trace_provider)
    tracer = trace.get_tracer(__name__)

    # Instrument smolagents with the configured provider
    SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)


set_telemetry()
search_tool = DuckDuckGoSearchTool()
agent = CodeAgent(
    tools=[search_tool],
    model=LiteLLMModel("openrouter/anthropic/claude-3.7-sonnet"),
)

agent.run("Hi, how are you?")
