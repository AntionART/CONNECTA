// Info panel state
let infoPanelOpen = false;
let contactPets = [];
let selectedPetId = null;
let currentPhone = null;

const speciesMap = {dog: 'Perro', cat: 'Gato', bird: 'Ave', rabbit: 'Conejo', other: 'Otro'};
const statusStyles = {
    scheduled: 'bg-blue-100 text-blue-700',
    confirmed: 'bg-green-100 text-green-700',
    completed: 'bg-gray-100 text-gray-700',
    cancelled: 'bg-red-100 text-red-700',
};
const statusLabels = {
    scheduled: 'Programada',
    confirmed: 'Confirmada',
    completed: 'Completada',
    cancelled: 'Cancelada',
};

// Toggle info panel
function toggleInfoPanel() {
    const panel = document.getElementById('info-panel');
    infoPanelOpen = !infoPanelOpen;

    if (infoPanelOpen) {
        panel.classList.remove('hidden');
        if (currentConversationId) {
            loadContactInfo();
        }
    } else {
        panel.classList.add('hidden');
    }
}

// Load contact info when conversation is selected
async function loadContactInfo() {
    const conv = conversations.find(c => c._id === currentConversationId);
    if (!conv) return;

    currentPhone = conv.phone_number;
    document.getElementById('info-contact-name').textContent = conv.contact_name || 'Sin nombre';
    document.getElementById('info-phone').textContent = conv.phone_number;

    await loadContactPets();
}

// Load pets for current contact phone
async function loadContactPets() {
    if (!currentPhone) return;

    const container = document.getElementById('info-pets-list');
    try {
        const res = await fetch(`/api/pets/by-phone/${currentPhone}`);
        contactPets = await res.json();

        if (contactPets.length === 0) {
            container.innerHTML = '<p class="text-xs text-gray-400">No hay mascotas registradas</p>';
            document.getElementById('btn-new-appointment').classList.add('hidden');
            document.getElementById('info-appointments-list').innerHTML = '<p class="text-xs text-gray-400">Agrega una mascota primero</p>';
            return;
        }

        document.getElementById('btn-new-appointment').classList.remove('hidden');
        renderContactPets();

        // Auto-select first pet
        if (!selectedPetId || !contactPets.find(p => p._id === selectedPetId)) {
            selectPet(contactPets[0]._id);
        }
    } catch (e) {
        container.innerHTML = '<p class="text-xs text-red-400">Error al cargar</p>';
    }
}

// Render pets list in info panel
function renderContactPets() {
    const container = document.getElementById('info-pets-list');
    container.innerHTML = contactPets.map(pet => {
        const isSelected = pet._id === selectedPetId;
        return `
            <div class="flex items-center justify-between p-2 rounded-md cursor-pointer mb-1 ${isSelected ? 'bg-indigo-50 border border-indigo-200' : 'hover:bg-gray-50 border border-transparent'}"
                 onclick="selectPet('${pet._id}')">
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900">${pet.name}</p>
                    <p class="text-xs text-gray-500">${speciesMap[pet.species] || pet.species}${pet.breed ? ' - ' + pet.breed : ''}</p>
                    <div class="flex gap-3 mt-0.5">
                        ${pet.age_years ? `<span class="text-xs text-gray-400">${pet.age_years} años</span>` : ''}
                        ${pet.weight_kg ? `<span class="text-xs text-gray-400">${pet.weight_kg} kg</span>` : ''}
                    </div>
                </div>
                <button onclick="event.stopPropagation(); editPetFromChat('${pet._id}')" class="text-gray-400 hover:text-indigo-600 ml-2" title="Editar">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                    </svg>
                </button>
            </div>
        `;
    }).join('');
}

// Select a pet and load its appointments
async function selectPet(petId) {
    selectedPetId = petId;
    renderContactPets();
    await loadPetAppointments(petId);
}

// Load appointments for selected pet
async function loadPetAppointments(petId) {
    const container = document.getElementById('info-appointments-list');
    container.innerHTML = '<p class="text-xs text-gray-400">Cargando...</p>';

    try {
        const res = await fetch(`/api/appointments/by-pet/${petId}`);
        const appointments = await res.json();

        if (appointments.length === 0) {
            container.innerHTML = '<p class="text-xs text-gray-400">No hay citas registradas</p>';
            return;
        }

        container.innerHTML = appointments.map(apt => {
            const date = apt.date ? new Date(apt.date).toLocaleString('es', {
                day: '2-digit', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit',
            }) : '-';
            const style = statusStyles[apt.status] || 'bg-gray-100 text-gray-700';
            const label = statusLabels[apt.status] || apt.status;

            return `
                <div class="p-2 rounded-md border border-gray-100 mb-2">
                    <div class="flex items-center justify-between mb-1">
                        <span class="text-xs font-medium text-gray-700">${date}</span>
                        <span class="text-xs px-1.5 py-0.5 rounded-full ${style}">${label}</span>
                    </div>
                    <p class="text-xs text-gray-600">${apt.reason}</p>
                    ${apt.veterinarian ? `<p class="text-xs text-gray-400 mt-0.5">Vet: ${apt.veterinarian}</p>` : ''}
                </div>
            `;
        }).join('');
    } catch (e) {
        container.innerHTML = '<p class="text-xs text-red-400">Error al cargar citas</p>';
    }
}

// --- Pet Modal from Chat ---

function openPetModalFromChat(petId = null) {
    document.getElementById('chat-pet-modal').classList.remove('hidden');
    document.getElementById('chat-pet-form').reset();
    document.getElementById('chat-pet-id').value = '';

    const conv = conversations.find(c => c._id === currentConversationId);
    document.getElementById('chat-pet-owner-name').value = conv?.contact_name || '';

    if (petId) {
        document.getElementById('chat-pet-modal-title').textContent = 'Editar mascota';
        const pet = contactPets.find(p => p._id === petId);
        if (pet) {
            document.getElementById('chat-pet-id').value = pet._id;
            document.getElementById('chat-pet-name').value = pet.name;
            document.getElementById('chat-pet-species').value = pet.species;
            document.getElementById('chat-pet-breed').value = pet.breed || '';
            document.getElementById('chat-pet-age').value = pet.age_years || '';
            document.getElementById('chat-pet-weight').value = pet.weight_kg || '';
            document.getElementById('chat-pet-owner-name').value = pet.owner_name || '';
        }
    } else {
        document.getElementById('chat-pet-modal-title').textContent = 'Nueva mascota';
    }
}

function closeChatPetModal() {
    document.getElementById('chat-pet-modal').classList.add('hidden');
}

function editPetFromChat(petId) {
    openPetModalFromChat(petId);
}

// Setup pet form
document.getElementById('chat-pet-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const petId = document.getElementById('chat-pet-id').value;
    const data = {
        name: document.getElementById('chat-pet-name').value,
        species: document.getElementById('chat-pet-species').value,
        breed: document.getElementById('chat-pet-breed').value,
        age_years: parseFloat(document.getElementById('chat-pet-age').value) || 0,
        weight_kg: parseFloat(document.getElementById('chat-pet-weight').value) || 0,
        owner_phone: currentPhone,
        owner_name: document.getElementById('chat-pet-owner-name').value,
    };

    const url = petId ? `/api/pets/${petId}` : '/api/pets';
    const method = petId ? 'PUT' : 'POST';

    const res = await fetch(url, {
        method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data),
    });

    if (res.ok) {
        closeChatPetModal();
        await loadContactPets();
    }
});

// --- Appointment Modal from Chat ---

function openAppointmentModalFromChat() {
    document.getElementById('chat-appointment-modal').classList.remove('hidden');
    document.getElementById('chat-appointment-form').reset();

    // Populate pet select with contact's pets
    const select = document.getElementById('chat-apt-pet');
    select.innerHTML = '<option value="">Seleccionar mascota</option>';
    contactPets.forEach(pet => {
        const opt = document.createElement('option');
        opt.value = pet._id;
        opt.textContent = `${pet.name} (${speciesMap[pet.species] || pet.species})`;
        if (pet._id === selectedPetId) opt.selected = true;
        select.appendChild(opt);
    });
}

function closeChatAppointmentModal() {
    document.getElementById('chat-appointment-modal').classList.add('hidden');
}

// Setup appointment form
document.getElementById('chat-appointment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        pet_id: document.getElementById('chat-apt-pet').value,
        date: document.getElementById('chat-apt-date').value,
        reason: document.getElementById('chat-apt-reason').value,
        veterinarian: document.getElementById('chat-apt-vet').value,
    };

    const res = await fetch('/api/appointments', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data),
    });

    if (res.ok) {
        closeChatAppointmentModal();
        // Reload appointments for the selected pet
        const petId = data.pet_id;
        if (petId) {
            selectedPetId = petId;
            await loadPetAppointments(petId);
            renderContactPets();
        }
    }
});

// Hook into conversation selection to load info panel
const _originalSelectConversation = selectConversation;
selectConversation = async function(conversationId) {
    await _originalSelectConversation(conversationId);
    if (infoPanelOpen) {
        loadContactInfo();
    }
};
