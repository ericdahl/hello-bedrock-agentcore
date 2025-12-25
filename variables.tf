variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "embedding_model_id" {
  description = "Bedrock embedding model ID for Knowledge Base"
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "chat_model_id" {
  description = "Bedrock chat model ID for RAG responses"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "enable_cloudfront" {
  description = "Enable CloudFront distribution for frontend hosting"
  type        = bool
  default     = false
}
