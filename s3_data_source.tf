# Data source bucket for product catalog
resource "aws_s3_bucket" "data_source" {
  bucket        = "${local.name_prefix}-data-source"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "data_source" {
  bucket = aws_s3_bucket.data_source.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_source" {
  bucket = aws_s3_bucket.data_source.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "data_files" {
  for_each = fileset("${path.module}/data", "**/*.md")

  bucket       = aws_s3_bucket.data_source.id
  key          = each.value
  source       = "${path.module}/data/${each.value}"
  etag         = filemd5("${path.module}/data/${each.value}")
  content_type = "text/markdown"
}
