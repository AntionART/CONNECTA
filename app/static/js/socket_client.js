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
        <p class="text-sm font-semibold text-gray-900">${title}</p>
        <p class="text-sm text-gray-600 mt-0.5">${message}</p>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Global new message notification (only when not on chat page or different conversation)
socket.on('new_message', (data) => {
    const msg = data.message;
    if (msg.direction === 'inbound') {
        const text = msg.content?.text || 'Nuevo mensaje';
        const preview = text.length > 50 ? text.substring(0, 50) + '...' : text;

        // Only show toast if not viewing this conversation
        if (typeof currentConversationId === 'undefined' || currentConversationId !== data.conversation_id) {
            showToast('Nuevo mensaje', preview);
        }
    }
});
