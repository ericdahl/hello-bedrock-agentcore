(function() {
    'use strict';

    // Configuration
    const API_ENDPOINT = 'https://fnmvr11tsb.execute-api.us-east-1.amazonaws.com/dev/chat';

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
        messageDiv.className = `message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = formatMarkdown(content);

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMarkdown(text) {
        // Escape HTML to prevent XSS
        const escapeHtml = (str) => {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        };

        // Split into lines and process
        const lines = text.split('\n');
        let html = '';
        let inList = false;

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            const trimmed = line.trim();

            // Handle bullet points
            if (trimmed.startsWith('- ')) {
                if (!inList) {
                    html += '<ul>';
                    inList = true;
                }
                html += '<li>' + escapeHtml(trimmed.substring(2)) + '</li>';
            } else {
                if (inList) {
                    html += '</ul>';
                    inList = false;
                }
                if (trimmed) {
                    html += '<p>' + escapeHtml(trimmed) + '</p>';
                }
            }
        }

        if (inList) {
            html += '</ul>';
        }

        return html;
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
