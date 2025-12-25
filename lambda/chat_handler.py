import json
import os
import uuid
import boto3
from datetime import datetime

# Initialize clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
bedrock_runtime = boto3.client('bedrock-runtime')
agentcore_data = boto3.client('bedrock-agentcore')

# Environment variables
KNOWLEDGE_BASE_ID = os.environ['KNOWLEDGE_BASE_ID']
MEMORY_ID = os.environ['MEMORY_ID']
GUARDRAIL_ID = os.environ['GUARDRAIL_ID']
GUARDRAIL_VERSION = os.environ['GUARDRAIL_VERSION']
CHAT_MODEL_ARN = os.environ['CHAT_MODEL_ARN']


def lambda_handler(event, context):
    """Main Lambda handler for chat API."""
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        session_id = body.get('session_id') or str(uuid.uuid4())
        user_id = body.get('user_id', 'anonymous')

        if not user_message:
            return response(400, {'error': 'Message is required'})

        # Retrieve memory context
        memory_context = retrieve_memory(user_id, session_id)

        # Query knowledge base with RAG
        kb_response = bedrock_agent_runtime.retrieve_and_generate(
            input={'text': user_message},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': CHAT_MODEL_ARN,
                    'generationConfiguration': {
                        'guardrailConfiguration': {
                            'guardrailId': GUARDRAIL_ID,
                            'guardrailVersion': GUARDRAIL_VERSION
                        },
                        'inferenceConfig': {
                            'textInferenceConfig': {
                                'maxTokens': 1024,
                                'temperature': 0.7
                            }
                        }
                    }
                }
            }
        )

        assistant_message = kb_response['output']['text']
        citations = extract_citations(kb_response)

        # Store conversation in memory
        store_conversation(user_id, session_id, user_message, assistant_message)

        return response(200, {
            'message': assistant_message,
            'session_id': session_id,
            'citations': citations
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error'})


def retrieve_memory(user_id: str, session_id: str) -> str:
    """Retrieve relevant memory context for the conversation."""
    try:
        response = agentcore_data.retrieve_memory(
            memoryId=MEMORY_ID,
            actorId=user_id,
            sessionId=session_id,
            maxResults=5
        )

        memories = response.get('memories', [])
        if memories:
            return '\n'.join([m.get('content', '') for m in memories])
        return ''
    except Exception as e:
        print(f"Memory retrieval error: {e}")
        return ''


def store_conversation(user_id: str, session_id: str, user_msg: str, assistant_msg: str):
    """Store conversation turn in AgentCore Memory."""
    try:
        agentcore_data.create_event(
            memoryId=MEMORY_ID,
            actorId=user_id,
            sessionId=session_id,
            eventTimestamp=datetime.now().isoformat(),
            payload=[
                {
                    'conversational': {
                        'content': {'text': user_msg},
                        'role': 'USER'
                    }
                },
                {
                    'conversational': {
                        'content': {'text': assistant_msg},
                        'role': 'ASSISTANT'
                    }
                }
            ]
        )
    except Exception as e:
        print(f"Memory storage error: {e}")


def extract_citations(kb_response: dict) -> list:
    """Extract source citations from knowledge base response."""
    citations = []
    for citation in kb_response.get('citations', []):
        for ref in citation.get('retrievedReferences', []):
            location = ref.get('location', {})
            s3_location = location.get('s3Location', {})
            citations.append({
                'uri': s3_location.get('uri', ''),
                'content': ref.get('content', {}).get('text', '')[:200]
            })
    return citations


def response(status_code: int, body: dict) -> dict:
    """Build API Gateway response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body)
    }
