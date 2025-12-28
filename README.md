# Absurd Gadgets Customer Support Agent

A customer support chatbot powered by **AWS Bedrock AgentCore Runtime** and the **Strands agent framework**. Demonstrates Knowledge Base integration, AgentCore Memory, Guardrails, and custom tool execution with automatic observability.

## Architecture

```
Frontend (S3) → API Gateway → Lambda Proxy → AgentCore Runtime → Strands Agent → Tools
                                                     ↓
                                            Knowledge Base (RAG)
                                            AgentCore Memory
                                            Guardrails
                                            Custom Tools
```

### Components

- **Frontend**: Static site (S3) with vanilla HTML/CSS/JS
- **Lambda Proxy**: 90-line Python function that forwards requests to AgentCore Runtime
- **AgentCore Runtime**: Managed container runtime for AI agents
- **Strands Agent**: Lightweight agent framework (replaces 500+ lines of custom code)
- **Knowledge Base**: Bedrock Knowledge Base with product catalog (RAG)
- **Memory**: AgentCore Memory for conversation context and user preferences
- **Guardrails**: Content filtering and topic blocking
- **Custom Tools**: Inventory checking tool with live stock data

## Key Features

### 🚀 Simplified Implementation
- **90 lines** of agent code (vs 500+ lines custom orchestration)
- **85% code reduction** using Strands framework
- Model-driven conversation orchestration
- Automatic tool execution and planning

### 📊 Automatic Observability
- Sessions tracked in CloudWatch
- Distributed tracing with X-Ray
- Request/response logging
- Tool execution metrics
- No manual instrumentation required

### 🛠 Tools & Integrations
- **Knowledge Base**: RAG over product catalog and policies
- **Memory**: Conversation summaries and user preferences
- **Custom Tool**: Real-time inventory checking
- **Guardrails**: PII detection, profanity filtering, topic blocking

## Prerequisites

- AWS Account with Bedrock access (us-east-1)
- AWS CLI configured
- Terraform >= 1.0
- Python 3.11+ (for local agent development)
- Docker (optional, for local builds)

## Quick Start

### 1. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Deploy all AWS resources
terraform apply
```

This creates:
- S3 buckets (frontend, data source, vectors)
- Bedrock Knowledge Base
- AgentCore Memory
- Guardrails
- Lambda + API Gateway
- IAM roles and permissions

### 2. Deploy the Agent

```bash
cd agent

# Install dependencies (if developing locally)
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Deploy to AgentCore Runtime (uses AWS CodeBuild)
agentcore deploy --agent absurd_gadgets_support
```

The deployment:
- Packages the agent code
- Builds an ARM64 Docker container in CodeBuild
- Pushes to Amazon ECR
- Deploys to AgentCore Runtime
- Configures observability (CloudWatch, X-Ray)

**Deployment time**: ~1 minute

### 3. Access the Frontend

Get the frontend URL:
```bash
terraform output frontend_url
```

Open the URL in your browser and start chatting!

## Testing the Agent

### Sample Queries

**Product Information** (Knowledge Base):
```
"Tell me about the Quantum Socks"
"What's the price of the WiFi Toaster for Pets?"
"What's your return policy?"
"Do you offer warranties?"
```

**Inventory Check** (Custom Tool):
```
"Do you have Quantum Socks in stock?"
"How many Telepathic Remotes are available?"
"Is the Self-Peeling Banana in stock?"
```

**Memory** (Multi-turn conversation):
```
User: "I love products in blue"
Agent: [remembers preference]
User: "What do you recommend?"
Agent: [uses remembered preference]
```

**Guardrails** (Content filtering):
```
"Tell me about [competitor product]"  → Topic blocked
[Profanity]                           → Word filtered
"My credit card is 1234-5678-9012-3456" → PII detected
```

### Direct API Testing

```bash
# Get the API endpoint
API_ENDPOINT=$(terraform output -raw api_endpoint)

# Test a query
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"message": "Do you have Quantum Socks in stock?"}'
```

### Monitor with CloudWatch

View automatic observability:

```bash
# Get the GenAI Observability dashboard URL
echo "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core"
```

Or tail logs:
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/absurd_gadgets_support-eSb910GTDh-DEFAULT \
  --log-stream-name-prefix "2025/12/28/[runtime-logs]" \
  --follow
```

## Project Structure

```
.
├── agent/                      # AgentCore Runtime agent
│   ├── main.py                 # Strands agent definition
│   ├── server.py               # FastAPI server for Runtime
│   ├── tools/
│   │   └── inventory.py        # Custom inventory tool
│   ├── inventory_data.py       # Business logic (156 lines)
│   ├── config.py               # Environment configuration
│   ├── Dockerfile              # Container definition
│   └── requirements.txt        # Python dependencies
│
├── lambda/                     # Lambda proxy (API Gateway → AgentCore)
│   ├── agentcore_proxy.py      # 90-line proxy to Runtime
│   └── inventory_data.py       # Shared business logic
│
├── frontend/                   # Static website
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── data/                       # Knowledge Base data source
│   ├── products/               # Product catalog (Markdown)
│   └── policies/               # Return/warranty policies
│
├── *.tf                        # Terraform infrastructure
└── README.md
```

## Agent Code Overview

The Strands agent (`agent/main.py`) is remarkably simple:

```python
from strands import Agent
from tools.inventory import check_inventory

SYSTEM_PROMPT = """You are a helpful customer support agent for Absurd Gadgets..."""

agent = Agent(
    name="absurd-gadgets-support",
    system_prompt=SYSTEM_PROMPT,
    tools=[check_inventory]
)
```

That's it! The framework handles:
- Tool execution and planning
- Conversation orchestration
- Response generation
- Error handling

## Product Catalog

The demo includes 6 absurd products:

| Product | SKU | Price | Stock |
|---------|-----|-------|-------|
| Antigravity Coffee Mug | ACM-006 | $399.99 | 23 |
| Invisible Umbrella | IU-004 | $149.99 | 87 |
| Quantum Socks | QS-003 | $89.99 | 156 |
| Self-Peeling Banana | SPB-001 | $29.99 | 412 |
| Telepathic Remote | TRC-005 | $299.99 | 34 |
| WiFi Toaster for Pets | WTP-002 | $199.99 | 201 |

## Development

### Local Testing

Test the agent locally without deploying:

```bash
cd agent
source venv/bin/activate

# Run local development mode
agentcore deploy --local

# Invoke the agent
agentcore invoke '{"input": "Do you have Quantum Socks?"}'
```

### Faster Iteration

Use local Docker builds instead of CodeBuild:

```bash
# Requires Docker Desktop
agentcore deploy --local-build
```

This builds the container locally (~10 seconds) instead of using CodeBuild (~60 seconds).

### Update the Agent

After modifying agent code:

```bash
cd agent
agentcore deploy --agent absurd_gadgets_support
```

The frontend continues working - no changes needed.

## Observability

### CloudWatch GenAI Dashboard

Automatic tracking of:
- **Sessions**: Conversation threads with user context
- **Traces**: Request flow through agent components
- **Spans**: Individual operations (tool calls, KB retrieval, etc.)
- **Metrics**: Latency, error rates, tool execution counts

Access: `CloudWatch → GenAI Observability → Agent Core`

### Example Trace

```
AgentInvocation (4.2s)
├── MemoryRetrieval (0.3s)
├── ModelInference (2.1s)
├── ToolExecution.check_inventory (0.8s)
│   └── inventory_data.get_inventory (0.2s)
└── ModelInference (1.0s)
```

## Cost Estimate

**AgentCore Runtime** (demo usage):
- ~$0.06 per session
- 10 test sessions = $0.60
- 100 test sessions = $6.00
- Charged only when active (tear down when done = $0)

**Other AWS Services** (minimal for demo):
- Lambda: Free tier covers demo usage
- API Gateway: ~$0.01/day
- S3: Negligible (<$0.10/month)
- Knowledge Base: Free tier covers small datasets
- Total: **<$1/month** for occasional testing

**Production scaling**: AgentCore Runtime includes automatic scaling, load balancing, and session management - no manual infrastructure.

## Cleanup

### Remove AgentCore Runtime

```bash
cd agent
agentcore delete --agent absurd_gadgets_support
```

### Destroy Infrastructure

```bash
terraform destroy
```

Note: You may need to manually empty S3 buckets first if Terraform fails.

## Troubleshooting

### Agent deployment fails

```bash
# Check CodeBuild logs
aws logs tail /aws/codebuild/bedrock-agentcore-absurd_gadgets_support-builder --follow
```

### Frontend shows "Unable to connect"

Check the API endpoint:
```bash
curl -X POST $(terraform output -raw api_endpoint) \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Knowledge Base not returning results

The Knowledge Base ingestion takes 10-30 minutes on first deployment. Check status:

```bash
# Get the latest ingestion job
aws bedrock-agent get-data-source \
  --knowledge-base-id $(terraform output -raw knowledge_base_id) \
  --data-source-id $(terraform output -raw data_source_id)
```

## Learn More

- [AWS Bedrock AgentCore](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [Strands Agent Framework](https://github.com/strands-agents/sdk-python)
- [Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)

## License

This is a demo project for learning purposes.
