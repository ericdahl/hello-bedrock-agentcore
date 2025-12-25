data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  name_prefix = "${local.name}-${var.environment}"
  account_id  = data.aws_caller_identity.current.account_id
  region      = data.aws_region.current.id

  embedding_model_arn = "arn:aws:bedrock:${local.region}::foundation-model/${var.embedding_model_id}"
  chat_model_arn      = "arn:aws:bedrock:${local.region}::foundation-model/${var.chat_model_id}"
}
