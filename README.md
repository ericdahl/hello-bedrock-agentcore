# AWS Bedrock AgentCore Demo

A chat interface demonstrating AWS Bedrock AgentCore with Knowledge Base, Memory, and Guardrails. Features an "Absurd Gadgets" product catalog for customer support interactions.

## Architecture

- **Frontend**: Vanilla HTML/CSS/JS (no build required)
- **Backend**: Lambda + API Gateway
- **Knowledge Base**: Bedrock KB with S3 Vectors storage
- **Memory**: AgentCore Memory for conversation context
- **Safety**: Bedrock Guardrails for content filtering

## Quick Start

### Prerequisites

- AWS account with Bedrock access (us-east-1 region)
- AWS CLI configured with credentials
- Terraform >= 1.0

### Deploy

1. **Clone and initialize**
   ```bash
   git clone <repo-url>
   cd hello-bedrock-agentcore
   terraform init
   ```

2. **Deploy infrastructure**
   ```bash
   terraform apply
   ```
   Review the plan and type `yes` to confirm.

3. **Upload mock data**
   ```bash
   ./scripts/sync_data.sh
   ```
   This uploads product catalog data and triggers Knowledge Base ingestion (takes 10-30 minutes).

4. **Start local dev server**
   ```bash
   ./scripts/local_dev.sh
   ```
   Open http://localhost:8080 in your browser.

### Test the Demo

Try these example queries:
- "Tell me about the Quantum Socks"
- "What's the price of the WiFi Toaster for Pets?"
- "What's your return policy?"
- "I bought a Self-Peeling Banana last week and it's amazing!" (tests memory)

**Test Guardrails:**
- Ask about competitor products (topic blocking)
- Try profanity (word filtering)
- Include credit card numbers (PII blocking)

**Inspect AgentCore Memory:**
- Open the UI and click "Show memory"
- Or call `GET /memory?user_id=web-user&session_id=<id>` on the API Gateway base URL

## Infrastructure

All infrastructure is defined in Terraform:
- `iam.tf` - IAM roles and policies
- `knowledge_base.tf` - Bedrock Knowledge Base with S3 Vectors
- `agentcore_memory.tf` - Conversation memory
- `guardrails.tf` - Content safety filters
- `lambda.tf` - Chat handler
- `api_gateway.tf` - REST API

## Mock Data

The demo includes 6 absurd products:
- Self-Peeling Banana ($29.99)
- WiFi-Enabled Toaster for Pets ($199.99)
- Quantum Socks ($89.99)
- Invisible Umbrella ($149.99)
- Telepathic Remote ($299.99)
- Antigravity Coffee Mug ($399.99)

Plus policy documents (warranty, pricing, returns).

## Cleanup

```bash
terraform destroy
```

Note: Manually delete the S3 buckets if they contain data.
