output "api_endpoint" {
  description = "API Gateway endpoint URL for chat"
  value       = "${aws_api_gateway_stage.chat.invoke_url}/chat"
}

output "frontend_bucket" {
  description = "S3 bucket for frontend hosting"
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_url" {
  description = "Frontend website URL"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID"
  value       = aws_bedrockagent_knowledge_base.product_catalog.id
}

output "data_source_bucket" {
  description = "S3 bucket for product catalog data"
  value       = aws_s3_bucket.data_source.bucket
}

output "data_source_id" {
  description = "Knowledge Base Data Source ID"
  value       = aws_bedrockagent_data_source.product_catalog.data_source_id
}

output "memory_id" {
  description = "AgentCore Memory ID"
  value       = aws_bedrockagentcore_memory.chat.id
}

output "guardrail_id" {
  description = "Bedrock Guardrail ID"
  value       = aws_bedrock_guardrail.demo.guardrail_id
}

output "s3_vectors_bucket" {
  description = "S3 Vectors bucket name"
  value       = aws_s3vectors_vector_bucket.kb.vector_bucket_name
}
