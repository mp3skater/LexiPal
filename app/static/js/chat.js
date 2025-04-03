const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
let isChatInitialized = false;
let conversationId = crypto.randomUUID();
let isNewConversation = true;


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

        // Add language review if available
        if (data.review) {
            addReviewMessage(data.review);
        }

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

function addReviewMessage(text) {
    // Clean up the response and ensure consistent formatting
    const formattedText = text
        .replace(/^-/gm, '•') // Replace any dashes with bullets
        .replace(/(\b(Grammar|Vocabulary|Possible Correction|Context):)/g, '<strong>$1</strong>') // Bold labels
        .replace(/\n/g, '<br>'); // Convert newlines to HTML breaks

    const reviewDiv = document.createElement('div');
    reviewDiv.className = 'review-message';
    reviewDiv.innerHTML = `
        <div class="review-header">Language Feedback</div>
        <div class="review-content">${formattedText}</div>
    `;
    chatMessages.appendChild(reviewDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


//SideBar
const textarea = document.getElementById('user-input');
if (textarea) {
    const initialHeight = textarea.scrollHeight;
    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto'; // Reset height
        let newHeight = textarea.scrollHeight;
        const maxHeight = 150; // Match CSS max-height
        if (newHeight > maxHeight) {
            newHeight = maxHeight;
            textarea.style.overflowY = 'auto'; // Show scrollbar
        } else {
            textarea.style.overflowY = 'hidden'; // Hide scrollbar
        }
        textarea.style.height = `${newHeight}px`;
    });
    
    // Initial adjustment in case of pre-filled content
    textarea.style.height = `${initialHeight}px`;
     if (initialHeight > 150) {
         textarea.style.overflowY = 'auto';
         textarea.style.height = '150px';
     } else {
         textarea.style.overflowY = 'hidden';
     }
}