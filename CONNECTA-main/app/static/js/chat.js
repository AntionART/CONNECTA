// Chat state
let currentConversationId = null;
let conversations = [];
let allLabels = [];
let allUsers = [];
let currentFilter = 'all';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadConversations();
    loadLabels();
    loadUsers();
    setupMessageForm();
    setupSearch();
});

// Load conversations list
async function loadConversations() {
    const statusParam = currentFilter !== 'all' ? `?status=${currentFilter}` : '';
    const res = await fetch(`/api/conversations${statusParam}`);
    conversations = await res.json();
    renderConversationList();
}

// Load available labels
async function loadLabels() {
    const res = await fetch('/api/labels');
    allLabels = await res.json();
}

// Load users for assignment
async function loadUsers() {
    const res = await fetch('/api/users');
    allUsers = await res.json();
    renderAgentSelect();
}

// Render conversation list in sidebar
function renderConversationList() {
    const container = document.getElementById('conversations-list');
    const searchTerm = document.getElementById('search-conversations')?.value?.toLowerCase() || '';

    const filtered = conversations.filter(conv => {
        const name = (conv.contact_name || conv.phone_number || '').toLowerCase();
        const lastMsg = (conv.last_message?.text || '').toLowerCase();
        return name.includes(searchTerm) || lastMsg.includes(searchTerm);
    });

    if (filtered.length === 0) {
        container.innerHTML = '<div class="empty-state py-12"><p class="text-sm">No hay conversaciones</p></div>';
        return;
    }

    container.innerHTML = filtered.map(conv => {
        const isActive = currentConversationId === conv._id;
        const name = conv.contact_name || conv.phone_number;
        const initials = name.substring(0, 2).toUpperCase();
        const preview = conv.last_message?.text || '';
        const previewTruncated = preview.length > 40 ? preview.substring(0, 40) + '...' : preview;
        const time = conv.last_message?.timestamp ? formatTime(conv.last_message.timestamp) : '';
        const unread = conv.unread_count || 0;

        const labelsHtml = (conv.labels || []).map(labelName => {
            const label = allLabels.find(l => l.name === labelName);
            const color = label ? label.color : '#6B7280';
            return `<span class="label-tag" style="background-color: ${color}15; color: ${color}">${label ? label.display_name : labelName}</span>`;
        }).join('');

        return `
            <div class="conversation-item ${isActive ? 'active' : ''}" onclick="selectConversation('${conv._id}')">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center flex-shrink-0">
                        <span class="text-xs font-bold text-slate-500">${initials}</span>
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between">
                            <p class="text-sm font-semibold text-slate-900 truncate">${name}</p>
                            <span class="text-[10px] text-slate-400 flex-shrink-0 ml-2">${time}</span>
                        </div>
                        <div class="flex items-center justify-between mt-0.5">
                            <p class="text-xs text-slate-400 truncate">${previewTruncated}</p>
                            ${unread > 0 ? `<span class="nav-badge ml-2 flex-shrink-0">${unread}</span>` : ''}
                        </div>
                        ${labelsHtml ? `<div class="flex gap-1 mt-1.5">${labelsHtml}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Select and load a conversation
async function selectConversation(conversationId) {
    currentConversationId = conversationId;

    document.querySelectorAll('.conversation-item').forEach(el => el.classList.remove('active'));
    event?.target?.closest('.conversation-item')?.classList.add('active');

    document.getElementById('chat-header').classList.remove('hidden');
    document.getElementById('message-input-area').classList.remove('hidden');

    const convRes = await fetch(`/api/conversations/${conversationId}`);
    const conv = await convRes.json();

    const name = conv.contact_name || conv.phone_number;
    document.getElementById('chat-contact-name').textContent = name;
    document.getElementById('chat-phone').textContent = conv.phone_number;
    document.getElementById('chat-avatar-text').textContent = name.substring(0, 2).toUpperCase();

    const statusBtn = document.getElementById('btn-toggle-status');
    statusBtn.textContent = conv.status === 'open' ? 'Cerrar' : 'Reabrir';

    const agentSelect = document.getElementById('assign-agent');
    agentSelect.value = conv.assigned_to || '';

    renderChatLabels(conv.labels || []);
    await loadMessages(conversationId);
    loadConversations();
}

// Load messages for a conversation
async function loadMessages(conversationId) {
    const res = await fetch(`/api/conversations/${conversationId}/messages`);
    const data = await res.json();
    renderMessages(data.messages);
}

// Render messages in chat panel
function renderMessages(messages) {
    const container = document.getElementById('messages-container');

    if (messages.length === 0) {
        container.innerHTML = '<div class="empty-state"><p class="text-sm font-medium">No hay mensajes aun</p></div>';
        return;
    }

    container.innerHTML = messages.map(msg => {
        const isOutbound = msg.direction === 'outbound';
        const text = msg.content?.text || '';
        const time = formatTime(msg.timestamp);
        const statusIcon = isOutbound ? getStatusIcon(msg.status) : '';

        return `
            <div class="message-bubble ${isOutbound ? 'outbound' : 'inbound'}">
                <p>${escapeHtml(text)}</p>
                <div class="message-time ${isOutbound ? 'text-right' : ''}">${time} ${statusIcon}</div>
            </div>
        `;
    }).join('');

    container.scrollTop = container.scrollHeight;
}

// Setup message send form
function setupMessageForm() {
    document.getElementById('send-message-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('message-input');
        const text = input.value.trim();
        if (!text || !currentConversationId) return;

        input.value = '';

        const res = await fetch(`/api/conversations/${currentConversationId}/messages`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text}),
        });

        if (!res.ok) {
            input.value = text;
            showToast('Error', 'No se pudo enviar el mensaje');
        }
    });
}

// Setup search
function setupSearch() {
    document.getElementById('search-conversations').addEventListener('input', () => {
        renderConversationList();
    });
}

// Filter conversations by status
function filterConversations(status) {
    currentFilter = status;

    document.querySelectorAll('.conv-filter').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`.conv-filter[data-filter="${status}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    loadConversations();
}

// Agent assignment
function renderAgentSelect() {
    const select = document.getElementById('assign-agent');
    select.innerHTML = '<option value="">Sin asignar</option>';
    allUsers.forEach(user => {
        select.innerHTML += `<option value="${user._id}">${user.display_name}</option>`;
    });

    select.addEventListener('change', async () => {
        if (!currentConversationId) return;
        await fetch(`/api/conversations/${currentConversationId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({assigned_to: select.value || null}),
        });
    });
}

// Toggle conversation status
async function toggleConversationStatus() {
    if (!currentConversationId) return;
    const btn = document.getElementById('btn-toggle-status');
    const newStatus = btn.textContent.trim() === 'Cerrar' ? 'closed' : 'open';

    await fetch(`/api/conversations/${currentConversationId}`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status: newStatus}),
    });

    btn.textContent = newStatus === 'open' ? 'Cerrar' : 'Reabrir';
    loadConversations();
}

// Labels management
function toggleLabelsPanel() {
    const panel = document.getElementById('labels-panel');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) {
        renderAvailableLabels();
    }
}

function renderAvailableLabels() {
    const container = document.getElementById('available-labels');
    const conv = conversations.find(c => c._id === currentConversationId);
    const currentLabels = conv?.labels || [];

    container.innerHTML = allLabels.map(label => {
        const isActive = currentLabels.includes(label.name);
        return `
            <button onclick="toggleLabel('${label.name}')"
                    class="label-tag cursor-pointer transition-smooth ${isActive ? 'ring-2 ring-offset-1' : 'opacity-50 hover:opacity-80'}"
                    style="background-color: ${label.color}15; color: ${label.color}; ${isActive ? `--tw-ring-color: ${label.color}` : ''}">
                ${label.display_name}
            </button>
        `;
    }).join('');

    if (allLabels.length === 0) {
        container.innerHTML = '<p class="text-xs text-slate-400">No hay etiquetas creadas</p>';
    }
}

async function toggleLabel(labelName) {
    if (!currentConversationId) return;
    const conv = conversations.find(c => c._id === currentConversationId);
    let labels = [...(conv?.labels || [])];

    if (labels.includes(labelName)) {
        labels = labels.filter(l => l !== labelName);
    } else {
        labels.push(labelName);
    }

    await fetch(`/api/conversations/${currentConversationId}`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({labels}),
    });

    await loadConversations();
    renderChatLabels(labels);
    renderAvailableLabels();
}

function renderChatLabels(labels) {
    const container = document.getElementById('chat-labels');
    container.innerHTML = labels.map(labelName => {
        const label = allLabels.find(l => l.name === labelName);
        const color = label ? label.color : '#6B7280';
        return `<span class="label-tag" style="background-color: ${color}15; color: ${color}">${label ? label.display_name : labelName}</span>`;
    }).join('');
}

// Socket events for real-time updates
socket.on('new_message', (data) => {
    if (data.conversation_id === currentConversationId) {
        const container = document.getElementById('messages-container');
        const msg = data.message;
        const isOutbound = msg.direction === 'outbound';
        const text = msg.content?.text || '';
        const time = formatTime(msg.timestamp);
        const statusIcon = isOutbound ? getStatusIcon(msg.status) : '';

        const emptyState = container.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${isOutbound ? 'outbound' : 'inbound'}`;
        bubble.innerHTML = `
            <p>${escapeHtml(text)}</p>
            <div class="message-time ${isOutbound ? 'text-right' : ''}">${time} ${statusIcon}</div>
        `;
        container.appendChild(bubble);
        container.scrollTop = container.scrollHeight;
    }

    loadConversations();
});

socket.on('conversation_updated', (conv) => {
    const idx = conversations.findIndex(c => c._id === conv._id);
    if (idx >= 0) {
        conversations[idx] = conv;
    } else {
        conversations.unshift(conv);
    }
    renderConversationList();
});

// Utility functions
function formatTime(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();

    if (isToday) {
        return date.toLocaleTimeString('es', {hour: '2-digit', minute: '2-digit'});
    }
    return date.toLocaleDateString('es', {day: '2-digit', month: '2-digit'});
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getStatusIcon(status) {
    const icons = {
        sent: '&#10003;',
        delivered: '&#10003;&#10003;',
        read: '<span class="text-blue-300">&#10003;&#10003;</span>',
    };
    return icons[status] || '';
}
