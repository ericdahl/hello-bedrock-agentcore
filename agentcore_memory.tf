resource "aws_bedrockagentcore_memory" "chat" {
  name                  = replace("${local.name_prefix}_memory", "-", "_")
  description           = "Conversation memory for Absurd Gadgets customer support"
  event_expiry_duration = 30
}

resource "aws_bedrockagentcore_memory_strategy" "session_summary" {
  memory_id  = aws_bedrockagentcore_memory.chat.id
  name       = "SessionSummary"
  type       = "SUMMARIZATION"
  namespaces = ["/summaries/{actorId}/{sessionId}"]
}

resource "aws_bedrockagentcore_memory_strategy" "user_preferences" {
  memory_id  = aws_bedrockagentcore_memory.chat.id
  name       = "UserPreferences"
  type       = "USER_PREFERENCE"
  namespaces = ["/preferences/{actorId}"]
}
