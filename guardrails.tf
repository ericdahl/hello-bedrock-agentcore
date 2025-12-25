resource "aws_bedrock_guardrail" "demo" {
  name                      = "${local.name_prefix}-guardrail"
  description               = "Guardrail for Absurd Gadgets product support demo"
  blocked_input_messaging   = "I apologize, but I can only help with questions about our Absurd Gadgets products."
  blocked_outputs_messaging = "I apologize, but I cannot provide that type of response. Please ask about our products!"

  # Content filters for harmful content
  content_policy_config {
    filters_config {
      type            = "HATE"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "INSULTS"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "SEXUAL"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "VIOLENCE"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "MISCONDUCT"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
  }

  # Sensitive information filtering
  sensitive_information_policy_config {
    pii_entities_config {
      type   = "EMAIL"
      action = "ANONYMIZE"
    }
    pii_entities_config {
      type   = "PHONE"
      action = "ANONYMIZE"
    }
    pii_entities_config {
      type   = "CREDIT_DEBIT_CARD_NUMBER"
      action = "BLOCK"
    }
    pii_entities_config {
      type   = "US_SOCIAL_SECURITY_NUMBER"
      action = "BLOCK"
    }
  }

  # Topic restrictions
  topic_policy_config {
    topics_config {
      name       = "Competitor Products"
      definition = "Questions about competitor products or comparisons with real products"
      examples   = ["What about Apple products?", "Is this better than a Samsung device?"]
      type       = "DENY"
    }
  }

  # Word filters
  word_policy_config {
    managed_word_lists_config {
      type = "PROFANITY"
    }
  }
}

resource "aws_bedrock_guardrail_version" "demo" {
  guardrail_arn = aws_bedrock_guardrail.demo.guardrail_arn
  description   = "Initial version"
}
