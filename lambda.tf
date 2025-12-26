data "archive_file" "lambda_chat" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/.terraform/lambda_chat.zip"
}

resource "aws_cloudwatch_log_group" "lambda_chat" {
  name              = "/aws/lambda/${local.name_prefix}-chat"
  retention_in_days = 7
}

resource "aws_lambda_function" "chat" {
  filename         = data.archive_file.lambda_chat.output_path
  function_name    = "${local.name_prefix}-chat"
  role             = aws_iam_role.lambda_chat.arn
  handler          = "chat_handler.lambda_handler"
  source_code_hash = data.archive_file.lambda_chat.output_base64sha256
  runtime          = "python3.12"
  timeout          = 45
  memory_size      = 256

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = aws_bedrockagent_knowledge_base.product_catalog.id
      MEMORY_ID         = aws_bedrockagentcore_memory.chat.id
      GUARDRAIL_ID      = aws_bedrock_guardrail.demo.guardrail_id
      GUARDRAIL_VERSION = aws_bedrock_guardrail_version.demo.version
      CHAT_MODEL_ARN    = local.chat_model_arn
      REGION            = local.region
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda_chat]
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chat.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.chat.execution_arn}/*/*"
}
