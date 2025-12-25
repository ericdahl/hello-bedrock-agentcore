data "aws_bedrock_foundation_model" "embedding" {
  model_id = var.embedding_model_id
}

resource "aws_bedrockagent_knowledge_base" "product_catalog" {
  name     = "${local.name_prefix}-kb"
  role_arn = aws_iam_role.bedrock_kb.arn

  description = "Absurd Gadgets product catalog knowledge base for customer support"

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = data.aws_bedrock_foundation_model.embedding.model_arn
    }
  }

  storage_configuration {
    type = "S3_VECTORS"
    s3_vectors_configuration {
      vector_bucket_arn = aws_s3vectors_vector_bucket.kb.vector_bucket_arn
      index_name        = aws_s3vectors_index.kb.index_name
    }
  }
}

resource "aws_bedrockagent_data_source" "product_catalog" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.product_catalog.id
  name              = "product-catalog-s3"

  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.data_source.arn
    }
  }

  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = "FIXED_SIZE"
      fixed_size_chunking_configuration {
        max_tokens         = 200
        overlap_percentage = 10
      }
    }
  }
}

# Trigger ingestion when data files change
resource "terraform_data" "kb_ingestion_trigger" {
  triggers_replace = {
    data_files = sha256(jsonencode([for k, v in aws_s3_object.data_files : v.etag]))
  }

  provisioner "local-exec" {
    command = <<-EOT
      echo "Triggering Knowledge Base ingestion..."
      aws bedrock-agent start-ingestion-job \
        --knowledge-base-id ${aws_bedrockagent_knowledge_base.product_catalog.id} \
        --data-source-id ${aws_bedrockagent_data_source.product_catalog.data_source_id}
    EOT
  }

  depends_on = [aws_s3_object.data_files]
}
