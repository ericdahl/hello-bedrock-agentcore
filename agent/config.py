"""Configuration for the Absurd Gadgets support agent."""
import os

# Bedrock service IDs (loaded from environment variables)
KNOWLEDGE_BASE_ID = os.environ.get('KNOWLEDGE_BASE_ID', '')
MEMORY_ID = os.environ.get('MEMORY_ID', '')
GUARDRAIL_ID = os.environ.get('GUARDRAIL_ID', '')
GUARDRAIL_VERSION = os.environ.get('GUARDRAIL_VERSION', '1')
