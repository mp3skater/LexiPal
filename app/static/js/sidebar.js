// static/js/sidebar.js

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const openBtn = document.getElementById('open-sidebar-btn');
    const closeBtn = document.getElementById('close-sidebar-btn');
    const mainContent = document.getElementById('main-content');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('user-input');
    const personaName = document.getElementById('persona-name');
    const newChatBtn = document.getElementById('new-chat-btn');

    // Function to open the sidebar
    function openSidebar() {
        if (sidebar && mainContent && openBtn) {
            loadChatHistory();
            sidebar.classList.add('open');
            mainContent.classList.add('shifted');
            localStorage.setItem('sidebarState', 'open');
            if (closeBtn) closeBtn.focus();
        }
    }

    // Function to close the sidebar
    function closeSidebar() {
        if (sidebar && mainContent && openBtn) {
            sidebar.classList.remove('open');
            mainContent.classList.remove('shifted');
            localStorage.setItem('sidebarState', 'closed');
            if (openBtn) openBtn.focus();
        }
    }

    // Event listeners for buttons
    if (openBtn) {
        openBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            openSidebar();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            closeSidebar();
        });
    }

    // Close sidebar if clicked outside
    if (mainContent) {
        mainContent.addEventListener('click', (event) => {
            if (sidebar && sidebar.classList.contains('open') &&
                !sidebar.contains(event.target) &&
                !openBtn.contains(event.target)) {
                closeSidebar();
            }
        });
    }

    // Close sidebar with Escape key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });

    // Check initial sidebar state
    const savedState = localStorage.getItem('sidebarState');
    if (savedState === 'open' && sidebar && mainContent && openBtn) {
        sidebar.style.transition = 'none';
        mainContent.style.transition = 'none';
        sidebar.classList.add('open');
        mainContent.classList.add('shifted');
        void sidebar.offsetWidth; // Force reflow
        sidebar.style.transition = '';
        mainContent.style.transition = '';
    }

    // Textarea auto-resize logic
    if (chatInput) {
        const initialHeight = chatInput.scrollHeight;
        const maxHeight = 150;

        const adjustTextareaHeight = () => {
            chatInput.style.height = 'auto';
            let newHeight = chatInput.scrollHeight;
            chatInput.style.overflowY = newHeight > maxHeight ? 'auto' : 'hidden';
            chatInput.style.height = `${Math.min(newHeight, maxHeight)}px`;
        };

        chatInput.addEventListener('input', adjustTextareaHeight);
        adjustTextareaHeight();
    }

    // Chat history functions
    async function loadChatHistory() {
        try {
            const response = await fetch('/api/chats', {
                credentials: 'include'
            });
            const chats = await response.json();
            renderChatHistory(chats);
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    function renderChatHistory(chats) {
        const historyList = document.getElementById('chat-history-list');
        historyList.innerHTML = chats.map(chat => `
            <li data-chat-id="${chat.conversation_id}" class="chat-item">
                <div class="persona">${chat.persona}</div>
                <div class="timestamp">${new Date(chat.created_at).toLocaleDateString()}</div>
                <div class="preview">${chat.preview}</div>
            </li>
        `).join('');

        document.querySelectorAll('.chat-item').forEach(item => {
            item.addEventListener('click', async (e) => {
                e.preventDefault();
                await loadChat(item.dataset.chatId);
                closeSidebar();
            });
        });
    }

    async function loadChat(conversationId) {
        try {
            const response = await fetch(`/api/chats/${conversationId}`, {
                credentials: 'include'
            });
            const chat = await response.json();

            // Reset chat interface
            chatMessages.innerHTML = '';
            window.conversationId = conversationId;
            window.isNewConversation = false;

            // Restore history
            chat.history.forEach(message => {
                addMessage(message.user, 'user');
                addMessage(message.bot, 'bot');
            });

            // Update persona name
            if (personaName) {
                personaName.textContent = chat.persona;
            }
        } catch (error) {
            console.error('Failed to load chat:', error);
            alert('Failed to load chat: ' + error.message);
        }
    }

}); // End of DOMContentLoaded