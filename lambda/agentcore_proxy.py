"""Lambda proxy for AgentCore Runtime."""
import json
import logging
import os
import boto3
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AgentCore client (AWS_REGION is automatically available in Lambda)
agentcore = boto3.client('bedrock-agentcore')

# Get runtime ID from environment
RUNTIME_ID = os.environ['RUNTIME_ID']


def lambda_handler(event, context):
    """Proxy requests to AgentCore Runtime."""
    try:
        # Parse request body (API Gateway may pass it as string or dict)
        body = event.get('body', '{}')
        logger.info(f"Raw body type: {type(body)}, content: {repr(body)[:200]}")

        if isinstance(body, str):
            body = json.loads(body)
        message = body.get('message', '')
        session_id = body.get('session_id')

        logger.info(f"Proxying request to AgentCore Runtime: {RUNTIME_ID}")
        logger.info(f"Message: {message}, Session: {session_id}")

        # Build payload for AgentCore Runtime
        payload = {'input': message}
        if session_id:
            payload['sessionId'] = session_id

        # Construct AgentCore Runtime ARN
        region = os.environ.get('AWS_REGION', 'us-east-1')
        account_id = context.invoked_function_arn.split(':')[4]
        runtime_arn = f"arn:aws:bedrock-agentcore:{region}:{account_id}:runtime/{RUNTIME_ID}"

        # Invoke AgentCore Runtime
        response = agentcore.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            payload=json.dumps(payload)
        )

        # Read the streaming response body
        response_payload = json.loads(response['response'].read())

        response_body = response_payload.get('output', {})
        response_message = response_body.get('message', {})
        response_content = response_message.get('content', [])

        # Extract text from content
        response_text = ''
        for item in response_content:
            if 'text' in item:
                response_text = item['text']
                break

        # Get session ID from response
        response_session_id = response_payload.get('sessionId', session_id or 'new-session')

        # Return response in format expected by frontend
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'message': response_text,
                'session_id': response_session_id
            })
        }

    except ClientError as e:
        logger.error(f"AgentCore error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f"AgentCore error: {str(e)}"
            })
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
