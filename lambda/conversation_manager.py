"""
Conversation management with Bedrock converse API and tool support.
Handles multi-turn conversations and tool execution loops.
"""

import json
from tool_handlers import execute_tool


def handle_conversation_turn(bedrock_runtime, model_id, user_message, memory_context, tool_config, guardrail_config):
    """
    Handle a single conversation turn with tool support.

    Args:
        bedrock_runtime: Boto3 bedrock-runtime client
        model_id: Model ARN or ID to use
        user_message: User's message text
        memory_context: Previous conversation context from memory
        tool_config: Tool definitions for converse API
        guardrail_config: Guardrail configuration

    Returns:
        dict: Response with 'message' and optionally 'tool_calls'
    """
    # Build messages list
    messages = []

    # Add user message
    messages.append({
        "role": "user",
        "content": [{"text": user_message}]
    })

    # System prompt for the assistant
    system_messages = [{
        "text": """You are a helpful customer support agent for Absurd Gadgets.

When customers ask about product availability, stock levels, or inventory:
- Use the check_inventory tool to get real-time accurate information
- The tool works with product names (e.g., "Quantum Socks") or SKU codes (e.g., "QS-003")
- In multi-turn conversations, understand context clues like "what about umbrella?" or "and socks?"

For other questions about products (features, pricing, policies, specifications):
- Answer based on your knowledge and training
- Be friendly, concise, and helpful

If you have access to user preferences or conversation context in the system messages:
- Use that information to provide personalized responses
- Remember details the user has shared about their preferences

Always provide accurate, helpful responses in a conversational manner."""
    }]

    # Add memory context if available
    if memory_context:
        system_messages.append({
            "text": f"Previous conversation context: {memory_context}"
        })

    tool_calls_made = []
    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"[Converse] Iteration {iteration}, calling model with {len(messages)} messages")

        # Call Bedrock converse API
        try:
            response = bedrock_runtime.converse(
                modelId=model_id,
                messages=messages,
                system=system_messages,
                toolConfig=tool_config,
                guardrailConfig=guardrail_config,
                inferenceConfig={
                    "maxTokens": 1024,
                    "temperature": 0.7
                }
            )

            print(f"[Converse] Response stopReason: {response.get('stopReason')}")

            # Check stop reason
            stop_reason = response.get('stopReason')

            if stop_reason == 'end_turn':
                # Model finished, extract text response
                assistant_message = extract_text_from_response(response)
                print(f"[Converse] Final response: {assistant_message[:100]}...")
                return {
                    "message": assistant_message,
                    "tool_calls": tool_calls_made
                }

            elif stop_reason == 'tool_use':
                # Model wants to use a tool
                print("[Converse] Model requested tool use")

                # Add assistant's response (including tool use) to messages
                assistant_content = response['output']['message']['content']
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })

                # Execute tools and collect results
                tool_results = []
                for content_block in assistant_content:
                    if 'toolUse' in content_block:
                        tool_use = content_block['toolUse']
                        tool_name = tool_use['name']
                        tool_input = tool_use['input']
                        tool_use_id = tool_use['toolUseId']

                        print(f"[Converse] Executing tool: {tool_name}")

                        # Execute the tool
                        tool_result = execute_tool(tool_name, tool_input)

                        # Track tool calls
                        tool_calls_made.append({
                            "name": tool_name,
                            "input": tool_input,
                            "result": tool_result
                        })

                        # Format tool result for model
                        tool_results.append({
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [
                                    {"json": tool_result}
                                ]
                            }
                        })

                # Add tool results to messages for next iteration
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue loop to get final response from model

            else:
                # Unexpected stop reason
                print(f"[Converse] Unexpected stopReason: {stop_reason}")
                assistant_message = extract_text_from_response(response)
                return {
                    "message": assistant_message or "I apologize, but I encountered an unexpected issue. Please try again.",
                    "tool_calls": tool_calls_made
                }

        except Exception as e:
            print(f"[Converse] Error during conversation: {str(e)}")
            return {
                "message": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "tool_calls": tool_calls_made
            }

    # Max iterations reached
    print("[Converse] Max iterations reached")
    return {
        "message": "I apologize, but I need to stop here. Please try rephrasing your question.",
        "tool_calls": tool_calls_made
    }


def extract_text_from_response(response):
    """
    Extract text content from converse API response.

    Args:
        response: Converse API response dict

    Returns:
        str: Extracted text or empty string
    """
    try:
        content_blocks = response['output']['message']['content']
        text_parts = []
        for block in content_blocks:
            if 'text' in block:
                text_parts.append(block['text'])
        return ' '.join(text_parts)
    except (KeyError, TypeError) as e:
        print(f"[Converse] Error extracting text: {e}")
        return ""
