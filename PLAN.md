# AWS Bedrock AgentCore Demo - Implementation Plan
     
     ## Overview
     
     A chat interface demo showcasing AWS Bedrock AgentCore services with a Knowledge
      Base containing an "Absurd Gadgets" product catalog.
     
     ## Architecture
     
     ```
     Frontend (vanilla HTML/JS/CSS)
         |
         v
     API Gateway (REST)
         |
         v
     Lambda (Python 3.12)
         |
         +---> Bedrock Knowledge Base (S3 Vectors) <--- S3 Data Source (product
     catalog)
         +---> AgentCore Memory (conversation context)
         +---> Bedrock Guardrails (content safety)
     ```
     
     ## File Structure
     
     ```
     /Users/ecd/repos/hello-bedrock-agentcore/
     ├── main.tf                 # Provider config (existing)
     ├── variables.tf            # Input variables
     ├── outputs.tf              # Output values
     ├── locals.tf               # Computed locals
     ├── iam.tf                  # IAM roles/policies (using aws_iam_policy_document)
     ├── s3.tf                   # S3 buckets (data source, frontend)
     ├── s3_vectors.tf           # S3 Vectors bucket and index
     ├── knowledge_base.tf       # Bedrock Knowledge Base + data source
     ├── agentcore_memory.tf     # AgentCore Memory
     ├── guardrails.tf           # Bedrock Guardrails
     ├── lambda.tf               # Lambda function
     ├── api_gateway.tf          # API Gateway
     ├── cloudfront.tf           # CloudFront (optional, controlled by variable)
     ├── lambda/
     │   └── chat_handler.py     # Lambda handler
     ├── frontend/
     │   ├── index.html
     │   ├── styles.css
     │   └── app.js
     ├── data/
     │   ├── products/
     │   │   ├── self-peeling-banana.md
     │   │   ├── wifi-toaster-for-pets.md
     │   │   ├── quantum-socks.md
     │   │   ├── invisible-umbrella.md
     │   │   ├── telepathic-remote.md
     │   │   └── antigravity-coffee-mug.md
     │   └── policies/
     │       ├── warranty-terms.md
     │       ├── pricing-rules.md
     │       └── return-policy.md
     └── scripts/
         ├── sync_data.sh        # Upload data to S3 + trigger ingestion
         └── local_dev.sh        # Local frontend server
     ```
     
     ## Implementation Steps
     
     ### Phase 1: Core Infrastructure
     
     #### 1.1 Variables (`variables.tf`)
     - `environment` (default: "dev")
     - `embedding_model_id` (default: "amazon.titan-embed-text-v2:0")
     - `chat_model_id` (default: "anthropic.claude-3-sonnet-20240229-v1:0")
     - `enable_cloudfront` (default: false)
     
     #### 1.2 Locals (`locals.tf`)
     - Compute `name`, `name_prefix`, `account_id`, `region`
     - Model ARNs
     
     #### 1.3 IAM (`iam.tf`)
     Using `aws_iam_policy_document` data sources (per CLAUDE.md):
     - **Lambda execution role**: CloudWatch Logs, Bedrock KB (RetrieveAndGenerate),
     AgentCore Memory, Guardrails
     - **Bedrock KB role**: S3 data source access, embedding model, S3 Vectors access
     
     ### Phase 2: Storage
     
     #### 2.1 S3 Buckets (`s3.tf`)
     - `data_source` bucket: Product catalog markdown files
     - `frontend` bucket: Static website hosting
     
     #### 2.2 S3 Vectors (`s3_vectors.tf`)
     Native Terraform (v6.24.0+):
     ```hcl
     resource "aws_s3vectors_vector_bucket" "kb" {
       name = "${local.name_prefix}-vectors"
     }
     
     resource "aws_s3vectors_index" "kb" {
       vector_bucket_name = aws_s3vectors_vector_bucket.kb.name
       index_name         = "product-catalog"
       dimension          = 1024  # Titan Embed V2
       distance_metric    = "cosine"
     }
     ```
     
     ### Phase 3: Bedrock Knowledge Base
     
     #### 3.1 Knowledge Base (`knowledge_base.tf`)
     Native S3 Vectors support (v6.27.0+):
     ```hcl
     resource "aws_bedrockagent_knowledge_base" "product_catalog" {
       name     = "${local.name_prefix}-kb"
       role_arn = aws_iam_role.bedrock_kb.arn
     
       knowledge_base_configuration {
         type = "VECTOR"
         vector_knowledge_base_configuration {
           embedding_model_arn =
     data.aws_bedrock_foundation_model.embedding.model_arn
         }
       }
     
       storage_configuration {
         type = "S3_VECTORS"
         s3_vectors_configuration {
           bucket_arn = aws_s3vectors_vector_bucket.kb.arn
         }
       }
     }
     
     resource "aws_bedrockagent_data_source" "products" {
       knowledge_base_id = aws_bedrockagent_knowledge_base.product_catalog.id
       name              = "product-catalog"
       data_source_configuration {
         type = "S3"
         s3_configuration {
           bucket_arn = aws_s3_bucket.data_source.arn
         }
       }
     }
     ```
     
     ### Phase 4: AgentCore Memory
     
     #### 4.1 Memory (`agentcore_memory.tf`)
     ```hcl
     resource "aws_bedrockagentcore_memory" "chat" {
       name                  = "${local.name_prefix}-memory"
       event_expiry_duration = 86400  # 24 hours
     
       memory_strategies {
         summary_memory_strategy {
           name       = "SessionSummary"
           namespaces = ["/summaries/{actorId}/{sessionId}"]
         }
       }
     }
     ```
     
     ### Phase 5: Guardrails
     
     #### 5.1 Guardrails (`guardrails.tf`)
     ```hcl
     resource "aws_bedrock_guardrail" "demo" {
       name                      = "${local.name_prefix}-guardrail"
       blocked_input_messaging   = "I can only help with Absurd Gadgets products."
       blocked_outputs_messaging = "I cannot provide that response."
     
       content_policy_config {
         filters_config {
           type            = "HATE"
           input_strength  = "HIGH"
           output_strength = "HIGH"
         }
         # ... INSULTS, SEXUAL, VIOLENCE, MISCONDUCT
       }
     
       sensitive_information_policy_config {
         pii_entities_config {
           type   = "CREDIT_DEBIT_CARD_NUMBER"
           action = "BLOCK"
         }
         # ... EMAIL (ANONYMIZE), PHONE (ANONYMIZE)
       }
     
       topic_policy_config {
         topics_config {
           name       = "Competitor Products"
           definition = "Questions about competitor products"
           type       = "DENY"
         }
       }
     
       word_policy_config {
         managed_word_lists_config {
           type = "PROFANITY"
         }
       }
     }
     ```
     
     ### Phase 6: Lambda + API Gateway
     
     #### 6.1 Lambda (`lambda.tf`)
     - Python 3.12 runtime
     - Handler: `chat_handler.lambda_handler`
     - Environment: KB_ID, MEMORY_ID, GUARDRAIL_ID, MODEL_ARN
     
     #### 6.2 Lambda Handler (`lambda/chat_handler.py`)
     ```python
     # Uses:
     # - bedrock_agent_runtime.retrieve_and_generate() for RAG
     # - agentcore.create_event() / retrieve_memory() for memory
     # - Guardrail config passed to retrieve_and_generate
     ```
     
     #### 6.3 API Gateway (`api_gateway.tf`)
     - REST API with `/chat` POST endpoint
     - CORS support for local development
     - Lambda proxy integration
     
     ### Phase 7: Frontend
     
     #### 7.1 HTML/CSS/JS (`frontend/`)
     - Vanilla HTML5 with no build tools
     - CSS with gradient styling
     - JavaScript with fetch API for chat
     - Session ID stored in localStorage
     
     ### Phase 8: Mock Data
     
     #### 8.1 Products (`data/products/`)
     Absurd Gadgets theme - each file contains:
     - Product name, SKU, price, category
     - Description with silly features
     - Technical specifications
     - Pricing tiers
     - Warranty info
     - FAQ
     
     **Products:**
     1. Self-Peeling Banana - NanoPeel technology, body-heat activated
     2. WiFi-Enabled Toaster for Pets - PetToast app, paw-activated
     3. Quantum Socks - Superposition comfort, entangled pairs
     4. Invisible Umbrella - You can't see rain you don't believe in
     5. Telepathic Remote - Think to change channels
     6. Antigravity Coffee Mug - Never spills (floats away instead)
     
     #### 8.2 Policies (`data/policies/`)
     - warranty-terms.md - Ridiculous Reliability Guarantee
     - pricing-rules.md - Volume discounts, bundles
     - return-policy.md - 30-day quantum guarantee
     
     ### Phase 9: Deployment Scripts
     
     #### 9.1 sync_data.sh
     ```bash
     # Sync data/ to S3
     # Trigger KB ingestion job
     ```
     
     #### 9.2 local_dev.sh
     ```bash
     # Write API endpoint to frontend/config.js
     # Start python3 -m http.server 8080
     ```
     
     ## Outputs
     
     - `api_endpoint` - API Gateway URL
     - `frontend_url` - S3 website or CloudFront URL
     - `knowledge_base_id` - For manual ingestion if needed
     - `data_source_bucket` - For syncing data
     
     ## Key Dependencies
     
     - AWS Provider >= 6.27.0 (you have this)
     - S3 Vectors resources (v6.24.0+)
     - Bedrock KB S3 Vectors config (v6.27.0+)
     - AgentCore Memory resources (check availability)
     
     ## Testing Workflow
     
     1. `terraform apply`
     2. `./scripts/sync_data.sh` - Upload products, trigger ingestion
     3. `./scripts/local_dev.sh` - Test frontend locally
     4. Test guardrails with competitor questions, PII, profanity
     5. Test memory by having multi-turn conversations
     
     ## Notes
     
     - Knowledge Base ingestion takes ~10-30 min initially
     - S3 Vectors has lower cost than OpenSearch Serverless
     - AgentCore Memory Terraform resources may need verification - fallback to
     null_resource if needed
     - Guardrail version resource needed after initial creation
