#!/bin/bash
set -e

echo "========================================="
echo "Absurd Gadgets Data Sync Script"
echo "========================================="
echo ""

# Change to repo root
cd "$(dirname "$0")/.."

# Get bucket name from Terraform output
echo "Getting S3 data source bucket name..."
DATA_BUCKET=$(terraform output -raw data_source_bucket)
KB_ID=$(terraform output -raw knowledge_base_id)
DATA_SOURCE_ID=$(terraform output -raw data_source_id)

echo "Data bucket: $DATA_BUCKET"
echo "Knowledge Base ID: $KB_ID"
echo "Data Source ID: $DATA_SOURCE_ID"
echo ""

# Sync data directory to S3
echo "Syncing product data to S3..."
aws s3 sync data/ "s3://$DATA_BUCKET/" --delete

echo ""
echo "Data sync complete!"
echo ""

# Trigger knowledge base ingestion
echo "Triggering Knowledge Base ingestion job..."
INGESTION_JOB=$(aws bedrock-agent start-ingestion-job \
    --knowledge-base-id "$KB_ID" \
    --data-source-id "$DATA_SOURCE_ID" \
    --output json)

INGESTION_JOB_ID=$(echo "$INGESTION_JOB" | jq -r '.ingestionJob.ingestionJobId')

echo "Ingestion job started: $INGESTION_JOB_ID"
echo ""
echo "Monitor progress:"
echo "  aws bedrock-agent get-ingestion-job \\"
echo "    --knowledge-base-id $KB_ID \\"
echo "    --data-source-id $DATA_SOURCE_ID \\"
echo "    --ingestion-job-id $INGESTION_JOB_ID"
echo ""
echo "Or check the AWS Console:"
echo "  https://console.aws.amazon.com/bedrock/home?#/knowledge-bases/$KB_ID"
echo ""
echo "Note: Ingestion typically takes 10-30 minutes to complete."
