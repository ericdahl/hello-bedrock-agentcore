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

        # Always use converse API with tool - let Claude decide when to use it
        print(f"[Handler] Processing message with tool available")
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

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error'})


def retrieve_memory(user_id: str, session_id: str, query: str) -> str:
    """Retrieve relevant memory context for the conversation."""
    memory_parts = []

    print(f"[Memory] === RETRIEVE MEMORY START ===")
    print(f"[Memory] user_id: {user_id}, session_id: {session_id}, query: {query}")

    try:
        # Retrieve user preferences
        preferences_namespace = f"/preferences/{user_id}"
        print(f"[Memory] Retrieving preferences from: {preferences_namespace}")
        pref_response = agentcore_data.retrieve_memory_records(
            memoryId=MEMORY_ID,
            namespace=preferences_namespace,
            searchCriteria={
                'searchQuery': query,
                'topK': 3
            },
            maxResults=3
        )

        print(f"[Memory] Preferences API response: {pref_response}")
        pref_records = pref_response.get('memoryRecords', [])
        print(f"[Memory] Preference records count: {len(pref_records)}")
        if pref_records:
            print(f"[Memory] ✅ Found {len(pref_records)} preference records")
            for i, record in enumerate(pref_records):
                print(f"[Memory] Pref record {i+1}: {record}")
            preferences = '\n'.join([r.get('content', '') for r in pref_records])
            memory_parts.append(f"User Preferences:\n{preferences}")
        else:
            print(f"[Memory] ⚠️ No preference records found")
    except Exception as e:
        print(f"[Memory] ❌ Preference retrieval error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[Memory] Traceback: {traceback.format_exc()}")

    try:
        # Retrieve session summary memories
        summary_namespace = f"/summaries/{user_id}/{session_id}"
        print(f"[Memory] Retrieving summaries from: {summary_namespace}")
        summary_response = agentcore_data.retrieve_memory_records(
            memoryId=MEMORY_ID,
            namespace=summary_namespace,
            searchCriteria={
                'searchQuery': query,
                'topK': 5
            },
            maxResults=5
        )

        print(f"[Memory] Summaries API response: {summary_response}")
        summary_records = summary_response.get('memoryRecords', [])
        print(f"[Memory] Summary records count: {len(summary_records)}")
        if summary_records:
            print(f"[Memory] ✅ Found {len(summary_records)} summary records")
            for i, record in enumerate(summary_records):
                print(f"[Memory] Summary record {i+1}: {record}")
            summaries = '\n'.join([r.get('content', '') for r in summary_records])
            memory_parts.append(f"Conversation Context:\n{summaries}")
        else:
            print(f"[Memory] ⚠️ No summary records found")
    except Exception as e:
        print(f"[Memory] ❌ Summary retrieval error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[Memory] Traceback: {traceback.format_exc()}")

    final_context = '\n\n'.join(memory_parts) if memory_parts else ''
    print(f"[Memory] Final memory context length: {len(final_context)} chars")
    print(f"[Memory] Final memory context: {final_context[:500]}...")
    print(f"[Memory] === RETRIEVE MEMORY END ===")
    return final_context


def store_conversation(user_id: str, session_id: str, user_msg: str, assistant_msg: str):
    """Store conversation turn in AgentCore Memory."""
    print(f"[Memory] === STORE CONVERSATION START ===")
    print(f"[Memory] user_id: {user_id}, session_id: {session_id}")
    print(f"[Memory] user_msg: {user_msg[:100]}...")
    print(f"[Memory] assistant_msg: {assistant_msg[:100]}...")

    try:
        event_payload = [
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
        print(f"[Memory] Event payload: {event_payload}")
        print(f"[Memory] Calling create_event with memoryId: {MEMORY_ID}")

        create_response = agentcore_data.create_event(
            memoryId=MEMORY_ID,
            actorId=user_id,
            sessionId=session_id,
            eventTimestamp=datetime.now().isoformat(),
            payload=event_payload
        )
        print(f"[Memory] ✅ Event created successfully")
        print(f"[Memory] create_event response: {create_response}")
    except Exception as e:
        print(f"[Memory] ❌ Memory storage error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[Memory] Traceback: {traceback.format_exc()}")

    print(f"[Memory] === STORE CONVERSATION END ===")


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
