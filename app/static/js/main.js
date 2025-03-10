let isChatInitialized = false;

document.addEventListener('DOMContentLoaded', () => {
    // Show initial fixed message
    addSystemMessage("With who, in what language and about what would you like to talk about?");
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
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.response);
        }

        const data = await response.json();
        
        if (!isChatInitialized) {
            isChatInitialized = true;
        }

        addMessage(data.response, 'bot', data.persona);

    } catch (error) {
        addMessage(error.message || 'Communication error', 'error');
    }
}

function addSystemMessage(text) {
    const div = document.createElement('div');
    div.className = 'system-message bg-yellow-100 p-3 rounded mb-4';
    div.textContent = text;
    chatMessages.appendChild(div);
}