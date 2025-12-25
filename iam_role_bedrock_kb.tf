# Bedrock Knowledge Base Role

data "aws_iam_policy_document" "bedrock_kb_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${local.region}:${local.account_id}:knowledge-base/*"]
    }
  }
}

resource "aws_iam_role" "bedrock_kb" {
  name               = "${local.name_prefix}-bedrock-kb"
  assume_role_policy = data.aws_iam_policy_document.bedrock_kb_assume_role.json
}

data "aws_iam_policy_document" "bedrock_kb_policy" {
  # S3 Data Source Access
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::${local.name_prefix}-data-source",
      "arn:aws:s3:::${local.name_prefix}-data-source/*"
    ]
  }

  # Bedrock Foundation Model
  statement {
    actions = [
      "bedrock:InvokeModel"
    ]
    resources = [local.embedding_model_arn]
  }

  # S3 Vectors Access
  statement {
    actions = [
      "s3vectors:Query",
      "s3vectors:QueryVectors",
      "s3vectors:GetVectors",
      "s3vectors:GetVectorBucket",
      "s3vectors:GetIndex",
      "s3vectors:PutVectorData",
      "s3vectors:PutVectors"
    ]
    resources = [
      "arn:aws:s3vectors:${local.region}:${local.account_id}:bucket/${local.name_prefix}-vectors",
      "arn:aws:s3vectors:${local.region}:${local.account_id}:bucket/${local.name_prefix}-vectors/*"
    ]
  }
}

resource "aws_iam_role_policy" "bedrock_kb" {
  name   = "kb-permissions"
  role   = aws_iam_role.bedrock_kb.id
  policy = data.aws_iam_policy_document.bedrock_kb_policy.json
}
