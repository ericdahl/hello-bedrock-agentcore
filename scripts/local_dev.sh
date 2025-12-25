#!/bin/bash
set -e

echo "========================================="
echo "Absurd Gadgets Local Development Server"
echo "========================================="
echo ""

# Change to repo root
cd "$(dirname "$0")/.."

# Get API endpoint from Terraform
echo "Getting API Gateway endpoint..."
API_ENDPOINT=$(terraform output -raw api_endpoint 2>/dev/null || echo "http://localhost:3000/chat")

echo "API Endpoint: $API_ENDPOINT"
echo ""

# Update frontend with API endpoint
echo "Updating frontend configuration..."
cat > frontend/app.js.tmp << EOF
(function() {
    'use strict';

    // Configuration
    const API_ENDPOINT = '$API_ENDPOINT';

    // State
    let sessionId = localStorage.getItem('sessionId') || generateUUID();
    localStorage.setItem('sessionId', sessionId);

    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');
    const loading = document.getElementById('loading');

    // Event Listeners
    chatForm.addEventListener('submit', handleSubmit);

    async function handleSubmit(e) {
        e.preventDefault();

        const message = messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';

        // Show loading state
        setLoading(true);

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId,
                    user_id: 'web-user'
                })
            });

            const data = await response.json();

            if (response.ok) {
                addMessage(data.message, 'assistant');
                sessionId = data.session_id;
                localStorage.setItem('sessionId', sessionId);
            } else {
                addMessage('Sorry, something went wrong. Please try again.', 'assistant');
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('Unable to connect. Please check your connection.', 'assistant');
        } finally {
            setLoading(false);
        }
    }

    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = \`message \${role}\`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function setLoading(isLoading) {
        sendButton.disabled = isLoading;
        loading.classList.toggle('hidden', !isLoading);
    }

    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
})();
EOF

mv frontend/app.js.tmp frontend/app.js

echo "Frontend configured!"
echo ""
echo "========================================="
echo "Starting local development server..."
echo "========================================="
echo ""
echo "Open your browser to: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
python3 -m http.server 8080
