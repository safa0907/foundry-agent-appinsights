"""
Azure AI Foundry Agent with Tools and Application Insights Tracing

This example demonstrates a more complete agent scenario with:
- Custom tool definitions
- Function calling
- Full tracing to Application Insights
"""

import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

os.environ["AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"] = "true"

from azure.ai.projects import AIProjectClient
from azure.ai.projects.telemetry import AIProjectInstrumentor
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace


# --- Define tools ---
def get_weather(city: str) -> str:
    """Simulate getting weather for a city."""
    weather_data = {
        "Riyadh": "45°C, Sunny",
        "Dubai": "42°C, Clear",
        "London": "18°C, Cloudy",
        "New York": "28°C, Partly Cloudy",
    }
    return weather_data.get(city, f"Weather data not available for {city}")


def get_time(city: str) -> str:
    """Simulate getting current time for a city."""
    from datetime import datetime, timezone, timedelta

    offsets = {
        "Riyadh": 3,
        "Dubai": 4,
        "London": 1,
        "New York": -4,
    }
    offset = offsets.get(city, 0)
    time = datetime.now(timezone(timedelta(hours=offset)))
    return time.strftime("%H:%M %Z")


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. Riyadh, London",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. Riyadh, London",
                    }
                },
                "required": ["city"],
            },
        },
    },
]

AVAILABLE_FUNCTIONS = {
    "get_weather": get_weather,
    "get_time": get_time,
}


def main():
    # --- Setup tracing ---
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential,
    )

    app_insights_connection_string = (
        project_client.telemetry.get_application_insights_connection_string()
    )
    if not app_insights_connection_string:
        app_insights_connection_string = os.environ.get(
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        )

    configure_azure_monitor(connection_string=app_insights_connection_string)
    AIProjectInstrumentor().instrument()

    tracer = trace.get_tracer(__name__)

    # --- Run agent with tools ---
    with tracer.start_as_current_span("agent-with-tools"):
        openai_client = project_client.get_openai_client()
        model_name = os.environ.get("FOUNDRY_MODEL_NAME", "gpt-5.4")

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Use the available tools to answer questions about weather and time.",
            },
            {
                "role": "user",
                "content": "What's the weather and current time in Riyadh?",
            },
        ]

        print("User: What's the weather and current time in Riyadh?\n")

        # First call - model may request tool calls
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        response_message = response.choices[0].message

        # Handle tool calls if present
        if response_message.tool_calls:
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"  [Tool Call] {function_name}({function_args})")

                # Execute the function
                function_response = AVAILABLE_FUNCTIONS[function_name](
                    **function_args
                )

                print(f"  [Tool Result] {function_response}")

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": function_response,
                    }
                )

            # Get final response after tool execution
            final_response = openai_client.chat.completions.create(
                model=model_name,
                messages=messages,
            )
            print(f"\nAssistant: {final_response.choices[0].message.content}")
        else:
            print(f"Assistant: {response_message.content}")

    print("\n--- Traces sent to Application Insights ---")
    print("Tool calls and responses are captured in the trace spans")


if __name__ == "__main__":
    main()
