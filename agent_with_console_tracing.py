"""
Azure AI Foundry Agent with Console Tracing (Local Development)

This example outputs traces to the console instead of Application Insights,
which is useful for local development and debugging.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"

from azure.ai.projects import AIProjectClient
from azure.ai.projects.telemetry import AIProjectInstrumentor
from azure.identity import DefaultAzureCredential
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


def main():
    # --- Configure console tracing ---
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # Enable instrumentation
    AIProjectInstrumentor().instrument()

    tracer = trace.get_tracer(__name__)

    # --- Create the AI Project Client ---
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential,
    )

    # --- Run agent with tracing ---
    with tracer.start_as_current_span("local-debug-conversation"):
        openai_client = project_client.get_openai_client()
        model_name = os.environ.get("FOUNDRY_MODEL_NAME", "gpt-5.4")

        print("User: Explain OpenTelemetry in one paragraph.")
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise technical assistant.",
                },
                {
                    "role": "user",
                    "content": "Explain OpenTelemetry in one paragraph.",
                },
            ],
        )
        print(f"Assistant: {response.choices[0].message.content}\n")

    print("\n--- Traces printed above in console output ---")
    print("For production, use agent_with_appinsights.py to send traces to App Insights")


if __name__ == "__main__":
    main()
