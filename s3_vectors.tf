resource "aws_s3vectors_vector_bucket" "kb" {
  vector_bucket_name = "${local.name_prefix}-vectors"
}

resource "aws_s3vectors_index" "kb" {
  vector_bucket_name = aws_s3vectors_vector_bucket.kb.vector_bucket_name
  index_name         = "product-catalog"
  dimension          = 1024
  distance_metric    = "cosine"
  data_type          = "float32"
}
