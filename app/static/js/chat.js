const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
let isChatInitialized = false;
let conversationId = crypto.randomUUID();
let isNewConversation = true;

const initialMessage = "With who, in what language and about what would you like to talk about?";
document.addEventListener('DOMContentLoaded', () => {
    addSystemMessage(initialMessage);
});

async function handleSubmit(e) {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    userInput.value = '';

    try {
        const endpoint = isChatInitialized ? '/chat' : '/start';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                conversation_id: conversationId,
                message: message
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.response || 'Request failed');
        }

        addMessage(data.response, 'bot');

        if (!isChatInitialized) {
            isChatInitialized = true;
        }

        // Update persona name if it's a new conversation
        if (isNewConversation) {
            const personaElement = document.getElementById('persona-name');
            if (personaElement) {
                personaElement.textContent = data.persona;
            }
            isNewConversation = false;
        }
    } catch (error) {
        addMessage(`Error: ${error.message}`, 'error');

        if (isNewConversation) {
            conversationId = crypto.randomUUID();
            isNewConversation = true;
        }
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender === 'user' ? 'user-message' : sender === 'bot' ? 'bot-message' : 'error-message'}`;
    messageDiv.innerHTML = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSystemMessage(text) {
    const div = document.createElement('div');
    div.className = 'system-message bg-yellow-100 p-3 rounded mb-4';
    div.textContent = text;
    chatMessages.appendChild(div);
}

chatForm.addEventListener('submit', handleSubmit);

userInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});