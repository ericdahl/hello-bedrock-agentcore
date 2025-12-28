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
  handler          = "agentcore_proxy.lambda_handler"
  source_code_hash = data.archive_file.lambda_chat.output_base64sha256
  runtime          = "python3.14"
  timeout          = 45
  memory_size      = 256

  environment {
    variables = {
      RUNTIME_ID = "absurd_gadgets_support-eSb910GTDh"
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
