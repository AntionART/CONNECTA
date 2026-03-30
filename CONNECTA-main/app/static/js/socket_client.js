// Global SocketIO client
const socket = io();

socket.on('connect', () => {
    console.log('Socket connected');
});

socket.on('disconnect', () => {
    console.log('Socket disconnected');
});

// Toast notification helper
function showToast(title, message) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-red-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
        </div>
        <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-slate-900">${title}</p>
            <p class="text-xs text-slate-500 mt-0.5 truncate">${message}</p>
        </div>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Global new message notification
socket.on('new_message', (data) => {
    const msg = data.message;
    if (msg.direction === 'inbound') {
        const text = msg.content?.text || 'Nuevo mensaje';
        const preview = text.length > 50 ? text.substring(0, 50) + '...' : text;

        if (typeof currentConversationId === 'undefined' || currentConversationId !== data.conversation_id) {
            showToast('Nuevo mensaje', preview);
        }

        // Update nav badge
        const badge = document.getElementById('nav-unread-badge');
        if (badge) {
            const count = parseInt(badge.textContent || '0') + 1;
            badge.textContent = count;
            badge.classList.remove('hidden');
        }
    }
});
