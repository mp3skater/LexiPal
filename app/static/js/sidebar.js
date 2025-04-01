// static/js/sidebar.js

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const openBtn = document.getElementById('open-sidebar-btn');
    const closeBtn = document.getElementById('close-sidebar-btn');
    const mainContent = document.getElementById('main-content');
    const chatMessagesContainer = document.getElementById('chat-messages');
    const chatInput = document.getElementById('user-input');
    const chatForm = document.getElementById('chat-form');
    const personaName = document.getElementById('persona-name');
    const newChatBtn = document.getElementById('new-chat-btn');

    // Function to open the sidebar
    function openSidebar() {
        if (sidebar && mainContent && openBtn) {
            sidebar.classList.add('open');
            mainContent.classList.add('shifted');
            // openBtn.style.opacity = '0'; // Faster visual feedback
            // openBtn.style.pointerEvents = 'none';
            localStorage.setItem('sidebarState', 'open');
            if(closeBtn) closeBtn.focus(); // Focus inside sidebar
        }
    }

    // Function to close the sidebar
    function closeSidebar() {
        if (sidebar && mainContent && openBtn) {
            sidebar.classList.remove('open');
            mainContent.classList.remove('shifted');
             // openBtn.style.opacity = '1'; // Faster visual feedback
             // openBtn.style.pointerEvents = 'auto';
            localStorage.setItem('sidebarState', 'closed');
             if(openBtn) openBtn.focus(); // Focus back on open button
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

    // Close sidebar if clicked outside (on main content area)
    if (mainContent) {
        mainContent.addEventListener('click', (event) => {
            // Check if sidebar is open and the click is not on the sidebar itself or the open button
            if (sidebar && sidebar.classList.contains('open') && !sidebar.contains(event.target) && !openBtn.contains(event.target)) {
                 // Option: Only close on mobile? Example: if (window.innerWidth < 768)
                 closeSidebar();
            }
        });
    }

    // Close sidebar with the Escape key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });

    // Check initial state from localStorage
    const savedState = localStorage.getItem('sidebarState');
    if (savedState === 'open' && sidebar && mainContent && openBtn) {
        // Apply state directly without animation for initial load
        sidebar.style.transition = 'none';
        mainContent.style.transition = 'none';
       // openBtn.style.transition = 'none'; // Disable transition initially

        sidebar.classList.add('open');
        mainContent.classList.add('shifted');
       // openBtn.style.opacity = '0';
       // openBtn.style.pointerEvents = 'none';

        // Force reflow/repaint before re-enabling transitions
        void sidebar.offsetWidth;

        sidebar.style.transition = '';
        mainContent.style.transition = '';
       // openBtn.style.transition = ''; // Re-enable transition
    }


    // --- Textarea Auto-Resize Logic (include if not in chat.js) ---
    if (chatInput) {
        const initialHeight = chatInput.scrollHeight;
        const maxHeight = 150; // Match CSS max-height

        const adjustTextareaHeight = () => {
             chatInput.style.height = 'auto'; // Temporarily shrink
            let newHeight = chatInput.scrollHeight;

            if (newHeight > maxHeight) {
                newHeight = maxHeight;
                chatInput.style.overflowY = 'auto';
            } else {
                chatInput.style.overflowY = 'hidden';
            }
            chatInput.style.height = `${newHeight}px`;
        };

        chatInput.addEventListener('input', adjustTextareaHeight);

        // Initial adjustment
        chatInput.style.overflowY = 'hidden'; // Start hidden
        adjustTextareaHeight(); // Run once on load
    }

});