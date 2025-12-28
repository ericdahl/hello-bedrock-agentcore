(function() {
    'use strict';

    // Configuration
    const API_ENDPOINT = window.API_CONFIG ? window.API_CONFIG.API_ENDPOINT : 'https://9bfzy6rl4h.execute-api.us-east-1.amazonaws.com/dev/chat';
    const MEMORY_ENDPOINT = API_ENDPOINT.endsWith('/chat') ? API_ENDPOINT.replace(/\/chat$/, '/memory') : `${API_ENDPOINT}/memory`;

    // State
    let sessionId = localStorage.getItem('sessionId') || generateUUID();
    localStorage.setItem('sessionId', sessionId);

    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');
    const loading = document.getElementById('loading');
    const memoryToggle = document.getElementById('memory-toggle');
    const memoryRefresh = document.getElementById('memory-refresh');
    const memoryOutput = document.getElementById('memory-output');

    // Event Listeners
    chatForm.addEventListener('submit', handleSubmit);
    memoryToggle.addEventListener('click', toggleMemoryPanel);
    memoryRefresh.addEventListener('click', refreshMemoryPanel);

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
                if (!memoryOutput.classList.contains('hidden')) {
                    refreshMemoryPanel();
                }
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

    function toggleMemoryPanel() {
        const isHidden = memoryOutput.classList.toggle('hidden');
        memoryRefresh.classList.toggle('hidden', isHidden);
        memoryToggle.textContent = isHidden ? 'Show memory' : 'Hide memory';
        if (!isHidden) {
            refreshMemoryPanel();
        }
    }

    async function refreshMemoryPanel() {
        memoryOutput.textContent = 'Loading memory...';
        try {
            const url = new URL(MEMORY_ENDPOINT);
            url.searchParams.set('user_id', 'web-user');
            url.searchParams.set('session_id', sessionId);
            const response = await fetch(url.toString(), { method: 'GET' });
            const data = await response.json();
            if (!response.ok) {
                memoryOutput.textContent = 'Unable to load memory.';
                return;
            }
            memoryOutput.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
            console.error('Error fetching memory:', error);
            memoryOutput.textContent = 'Unable to load memory.';
        }
    }

    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Use marked to parse markdown and DOMPurify to sanitize HTML
        const rawHtml = marked.parse(content);
        contentDiv.innerHTML = DOMPurify.sanitize(rawHtml);

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
