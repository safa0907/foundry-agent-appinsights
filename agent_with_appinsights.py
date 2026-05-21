"""
Azure AI Foundry Agent with Application Insights Tracing

This example demonstrates how to:
1. Connect to an Azure AI Foundry project
2. Enable OpenTelemetry tracing to Application Insights
3. Run a simple agent conversation with full observability
"""

import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)

# --- Step 1: Set the experimental tracing flag (required) ---
os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"

from azure.ai.projects import AIProjectClient
from azure.ai.projects.telemetry import AIProjectInstrumentor
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider


def main():
    # --- Step 2: Create the AI Project Client ---
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential,
    )

    # --- Step 3: Configure Application Insights tracing ---
    # Option A: Get connection string from your Foundry project (recommended)
    # This automatically pulls the App Insights connection string linked to your project
    app_insights_connection_string = (
        project_client.telemetry.get_application_insights_connection_string()
    )

    # Option B: Use connection string directly from environment variable
    # app_insights_connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]

    if not app_insights_connection_string:
        print("WARNING: No Application Insights connection string found.")
        print("Make sure App Insights is connected to your Foundry project.")
        print("Falling back to environment variable...")
        app_insights_connection_string = os.environ.get(
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        )

    configure_azure_monitor(connection_string=app_insights_connection_string)

    # --- Step 4: Enable instrumentation ---
    AIProjectInstrumentor().instrument()

    # --- Step 5: Create a tracer and run the agent ---
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("agent-conversation"):
        # Get an authenticated OpenAI client from the project
        openai_client = project_client.get_openai_client()

        model_name = os.environ.get("FOUNDRY_MODEL_NAME", "gpt-5.4")

        # First message
        print("User: What are the benefits of using Application Insights with AI agents?")
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful Azure cloud architect assistant.",
                },
                {
                    "role": "user",
                    "content": "What are the benefits of using Application Insights with AI agents?",
                },
            ],
        )
        assistant_reply = response.choices[0].message.content
        print(f"Assistant: {assistant_reply}\n")

        # Follow-up message
        print("User: How do I set up tracing for production?")
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful Azure cloud architect assistant.",
                },
                {
                    "role": "user",
                    "content": "What are the benefits of using Application Insights with AI agents?",
                },
                {"role": "assistant", "content": assistant_reply},
                {
                    "role": "user",
                    "content": "How do I set up tracing for production?",
                },
            ],
        )
        print(f"Assistant: {response.choices[0].message.content}\n")

    # --- Step 6: Force flush telemetry before exiting ---
    print("Flushing telemetry to Application Insights...")
    provider = trace.get_tracer_provider()
    if isinstance(provider, SdkTracerProvider):
        provider.force_flush(timeout_millis=10000)
    # Give the exporter a moment to send
    time.sleep(5)

    print("\n--- Traces sent to Application Insights ---")
    print("View them in the Foundry portal: Observability > Traces")
    print("Or in Azure Portal: Application Insights > Transaction search")
    print("(Traces may take 2-5 minutes to appear)")


if __name__ == "__main__":
    main()
