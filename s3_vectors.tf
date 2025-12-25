resource "aws_s3vectors_vector_bucket" "kb" {
  vector_bucket_name = "${local.name_prefix}-vectors"
  force_destroy      = true
}

resource "aws_s3vectors_index" "kb" {
  vector_bucket_name = aws_s3vectors_vector_bucket.kb.vector_bucket_name
  index_name         = "product-catalog"
  dimension          = 1024
  distance_metric    = "cosine"
  data_type          = "float32"

  metadata_configuration {
    non_filterable_metadata_keys = ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
  }
}
