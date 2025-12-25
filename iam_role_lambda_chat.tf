data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    sid     = "AllowLambdaServiceAssumeRole"
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
  statement {
    sid = "CloudWatchLogsAccess"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:${local.region}:${local.account_id}:*"]
  }

  statement {
    sid = "BedrockKnowledgeBaseAndModelsAccess"
    actions = [
      "bedrock:RetrieveAndGenerate",
      "bedrock:Retrieve",
      "bedrock:InvokeModel"
    ]
    resources = ["*"]
  }

  statement {
    sid = "AgentCoreMemoryAccess"
    actions = [
      "bedrock-agentcore:CreateEvent",
      "bedrock-agentcore:RetrieveMemoryRecords",
      "bedrock-agentcore:GetMemory"
    ]
    resources = ["*"]
  }

  statement {
    sid       = "BedrockGuardrailsAccess"
    actions   = ["bedrock:ApplyGuardrail"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "lambda_chat" {
  name   = "chat-permissions"
  role   = aws_iam_role.lambda_chat.id
  policy = data.aws_iam_policy_document.lambda_chat_policy.json
}
