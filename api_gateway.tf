resource "aws_api_gateway_rest_api" "chat" {
  name        = "${local.name_prefix}-chat-api"
  description = "Chat API for Absurd Gadgets product support"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "chat" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  parent_id   = aws_api_gateway_rest_api.chat.root_resource_id
  path_part   = "chat"
}

# /memory
resource "aws_api_gateway_resource" "memory" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  parent_id   = aws_api_gateway_rest_api.chat.root_resource_id
  path_part   = "memory"
}

# POST /chat
resource "aws_api_gateway_method" "chat_post" {
  rest_api_id   = aws_api_gateway_rest_api.chat.id
  resource_id   = aws_api_gateway_resource.chat.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "chat_post" {
  rest_api_id             = aws_api_gateway_rest_api.chat.id
  resource_id             = aws_api_gateway_resource.chat.id
  http_method             = aws_api_gateway_method.chat_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.chat.invoke_arn
}

# GET /memory
resource "aws_api_gateway_method" "memory_get" {
  rest_api_id   = aws_api_gateway_rest_api.chat.id
  resource_id   = aws_api_gateway_resource.memory.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "memory_get" {
  rest_api_id             = aws_api_gateway_rest_api.chat.id
  resource_id             = aws_api_gateway_resource.memory.id
  http_method             = aws_api_gateway_method.memory_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.chat.invoke_arn
}

# OPTIONS /chat (CORS)
resource "aws_api_gateway_method" "chat_options" {
  rest_api_id   = aws_api_gateway_rest_api.chat.id
  resource_id   = aws_api_gateway_resource.chat.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "chat_options" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "chat_options" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "chat_options" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  status_code = aws_api_gateway_method_response.chat_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# OPTIONS /memory (CORS)
resource "aws_api_gateway_method" "memory_options" {
  rest_api_id   = aws_api_gateway_rest_api.chat.id
  resource_id   = aws_api_gateway_resource.memory.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "memory_options" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  resource_id = aws_api_gateway_resource.memory.id
  http_method = aws_api_gateway_method.memory_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "memory_options" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  resource_id = aws_api_gateway_resource.memory.id
  http_method = aws_api_gateway_method.memory_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "memory_options" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  resource_id = aws_api_gateway_resource.memory.id
  http_method = aws_api_gateway_method.memory_options.http_method
  status_code = aws_api_gateway_method_response.memory_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}
resource "aws_api_gateway_deployment" "chat" {
  rest_api_id = aws_api_gateway_rest_api.chat.id
  triggers = {
    redeployment = sha1(jsonencode({
      resources = [
        aws_api_gateway_resource.chat.id,
        aws_api_gateway_resource.memory.id,
        aws_api_gateway_method.chat_post.id,
        aws_api_gateway_method.chat_options.id,
        aws_api_gateway_method.memory_get.id,
        aws_api_gateway_method.memory_options.id,
        aws_api_gateway_integration.chat_post.id,
        aws_api_gateway_integration.chat_options.id,
        aws_api_gateway_integration.memory_get.id,
        aws_api_gateway_integration.memory_options.id,
        aws_api_gateway_gateway_response.default_4xx.id,
        aws_api_gateway_gateway_response.default_5xx.id
      ]
    }))
  }

  depends_on = [
    aws_api_gateway_integration.chat_post,
    aws_api_gateway_integration.chat_options,
    aws_api_gateway_integration.memory_get,
    aws_api_gateway_integration.memory_options
  ]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "chat" {
  deployment_id = aws_api_gateway_deployment.chat.id
  rest_api_id   = aws_api_gateway_rest_api.chat.id
  stage_name    = var.environment
}

# Ensure CORS headers on error responses (e.g., auth/invalid request)
resource "aws_api_gateway_gateway_response" "default_4xx" {
  rest_api_id   = aws_api_gateway_rest_api.chat.id
  response_type = "DEFAULT_4XX"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
  }
}

resource "aws_api_gateway_gateway_response" "default_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.chat.id
  response_type = "DEFAULT_5XX"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
  }
}
