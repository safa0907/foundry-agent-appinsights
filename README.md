# Python Agent with Azure AI Foundry & Application Insights

This example demonstrates how to build a Python AI agent using Azure AI Foundry deployed models and connect it to Azure Application Insights for observability and tracing.

## Overview

The agent uses:
- **Azure AI Foundry** for model deployment (GPT-5.4)
- **Azure Application Insights** for tracing and monitoring
- **OpenTelemetry** for instrumentation

## Prerequisites

- Python 3.10+
- Azure subscription with:
  - An Azure AI Foundry project with a deployed model
  - An Application Insights resource connected to your Foundry project
- Azure CLI installed and logged in (`az login`)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/foundry-agent-appinsights-example.git
   cd foundry-agent-appinsights-example
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy the environment template and fill in your values:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your Application Insights connection string (found in Azure Portal > your App Insights resource > Overview).

## Running the Examples

### Basic Agent with Azure Monitor Tracing

```bash
python agent_with_appinsights.py
```

This runs a simple agent that:
- Creates a conversational agent using the Foundry-deployed model
- Instruments all calls with OpenTelemetry
- Exports traces to Application Insights

### Agent with Console Tracing (for local debugging)

```bash
python agent_with_console_tracing.py
```

This outputs traces to the console for local development.

## Viewing Traces

1. Go to the [Microsoft Foundry portal](https://ai.azure.com)
2. Open your project → **Observability** → **Traces**
3. Or view directly in **Azure Portal** → **Application Insights** → **Transaction search**

Traces typically appear within 2–5 minutes after agent execution.

## Architecture

```
┌──────────────┐       ┌─────────────────────┐       ┌──────────────────────┐
│  Python App  │──────▶│  Azure AI Foundry    │──────▶│  Application Insights │
│  (Agent)     │       │  (GPT-5.4 Model)    │       │  (Traces & Metrics)   │
└──────────────┘       └─────────────────────┘       └──────────────────────┘
       │                                                        ▲
       └────────── OpenTelemetry Instrumentation ──────────────┘
```

## Resources

- [Set up tracing in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-setup)
- [Configure tracing for AI agent frameworks](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-framework)
- [Agent tracing overview](https://learn.microsoft.com/en-us/azure/foundry/observability/concepts/trace-agent-concept)
- [Azure AI Projects Python SDK – Tracing](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python#tracing)
- [Enable Azure Monitor OpenTelemetry (Python)](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python)
- [SDK telemetry samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents/telemetry)

## License

MIT
