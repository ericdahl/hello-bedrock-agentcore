import json
import os
import uuid
import boto3
from datetime import datetime

# Initialize clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
bedrock_runtime = boto3.client('bedrock-runtime')
agentcore_data = boto3.client('bedrock-agentcore')

# Import tool calling modules
from tool_definitions import TOOL_CONFIG
from conversation_manager import handle_conversation_turn

# Environment variables
KNOWLEDGE_BASE_ID = os.environ['KNOWLEDGE_BASE_ID']
MEMORY_ID = os.environ['MEMORY_ID']
GUARDRAIL_ID = os.environ['GUARDRAIL_ID']
GUARDRAIL_VERSION = os.environ['GUARDRAIL_VERSION']
CHAT_MODEL_ARN = os.environ['CHAT_MODEL_ARN']

# Greeting detection patterns
GREETINGS = {
    'hello': 'Hello! I can help you learn about our Absurd Gadgets products. What would you like to know?',
    'hi': 'Hi there! Ask me anything about our wonderfully ridiculous products!',
    'hey': 'Hey! Ready to explore our absurd product lineup?',
    'good morning': 'Good morning! How can I help you with our Absurd Gadgets today?',
    'good afternoon': 'Good afternoon! What would you like to know about our products?',
    'good evening': 'Good evening! Ready to discover some absurdly amazing gadgets?',
    'greetings': 'Greetings! I\'m here to help you explore our Absurd Gadgets catalog.',
}


def handle_greeting(message: str) -> str:
    """Check if message is a greeting and return appropriate response."""
    normalized = message.lower().strip().rstrip('!.?')
    if normalized in GREETINGS:
        return GREETINGS[normalized]
    return None


def is_inventory_question(message: str) -> bool:
    """Detect if question is about stock/inventory."""
    inventory_keywords = [
        'stock', 'available', 'inventory', 'in stock',
        'how many', 'do you have', 'quantity', 'availability',
        'out of stock', 'restock', 'available for purchase'
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in inventory_keywords)


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

        # Handle common greetings
        greeting_message = handle_greeting(user_message)
        if greeting_message:
            return response(200, {
                'message': greeting_message,
                'session_id': session_id,
                'citations': []
            })

        # Retrieve memory context
        memory_context = retrieve_memory(user_id, session_id, user_message)

        # Route based on question type
        if is_inventory_question(user_message):
            print(f"[Router] Detected inventory question, using tool calling")
            # Use converse API with inventory tool
            response_data = handle_conversation_turn(
                bedrock_runtime=bedrock_runtime,
                model_id=CHAT_MODEL_ARN,
                user_message=user_message,
                memory_context=memory_context,
                tool_config=TOOL_CONFIG,
                guardrail_config={
                    'guardrailIdentifier': GUARDRAIL_ID,
                    'guardrailVersion': GUARDRAIL_VERSION
                }
            )
            assistant_message = response_data['message']
            tool_calls = response_data.get('tool_calls', [])

            # Store conversation in memory
            store_conversation(user_id, session_id, user_message, assistant_message)

            return response(200, {
                'message': assistant_message,
                'session_id': session_id,
                'tool_used': tool_calls[0]['name'] if tool_calls else None
            })
        else:
            print(f"[Router] Using Knowledge Base for product information")
            # Use existing KB retrieve_and_generate for product details
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


def retrieve_memory(user_id: str, session_id: str, query: str) -> str:
    """Retrieve relevant memory context for the conversation."""
    try:
        # Retrieve session summary memories
        namespace = f"/summaries/{user_id}/{session_id}"
        response = agentcore_data.retrieve_memory_records(
            memoryId=MEMORY_ID,
            namespace=namespace,
            searchCriteria={
                'searchQuery': query,
                'topK': 5
            },
            maxResults=5
        )

        records = response.get('memoryRecords', [])
        if records:
            return '\n'.join([r.get('content', '') for r in records])
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
