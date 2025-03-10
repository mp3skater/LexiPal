document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    let currentPersona = 'AI Assistant';

    // Initialize chat when page loads
    initializeChat();

    async function initializeChat() {
        try {
            const response = await fetch('/start', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            const data = await response.json();
            currentPersona = data.persona || 'AI Assistant';
            addMessage(data.response, 'bot', currentPersona);
        } catch (error) {
            addMessage('Error starting chat session', 'bot', currentPersona);
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        userInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ message }),
            });

            const data = await response.json();
            currentPersona = data.persona || currentPersona;
            addMessage(data.response, 'bot', currentPersona);
        } catch (error) {
            addMessage('Error communicating with server', 'bot', currentPersona);
        }
    }

    function addMessage(text, sender, persona = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message p-4 mb-4 rounded-lg`;
        messageDiv.innerHTML = `
            <div class="font-bold text-sm mb-1">${sender === 'bot' ? persona : 'You'}</div>
            <div class="text-gray-800">${text}</div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    chatForm.addEventListener('submit', handleSubmit);
});