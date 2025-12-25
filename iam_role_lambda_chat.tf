# Lambda Chat Execution Role

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_chat" {
  name               = "${local.name_prefix}-lambda-chat"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "lambda_chat_policy" {
  # CloudWatch Logs
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:${local.region}:${local.account_id}:*"]
  }

  # Bedrock Knowledge Base and Models
  statement {
    actions = [
      "bedrock:RetrieveAndGenerate",
      "bedrock:Retrieve",
      "bedrock:InvokeModel"
    ]
    resources = ["*"]
  }

  # AgentCore Memory
  statement {
    actions = [
      "bedrock-agentcore:CreateEvent",
      "bedrock-agentcore:RetrieveMemoryRecords",
      "bedrock-agentcore:GetMemory"
    ]
    resources = ["*"]
  }

  # Guardrails
  statement {
    actions = [
      "bedrock:ApplyGuardrail"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "lambda_chat" {
  name   = "chat-permissions"
  role   = aws_iam_role.lambda_chat.id
  policy = data.aws_iam_policy_document.lambda_chat_policy.json
}
