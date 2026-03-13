// Appointments management
let appointments = [];
let petsForSelect = [];
let currentStatusFilter = '';

document.addEventListener('DOMContentLoaded', () => {
    loadAppointments();
    loadPetsForSelect();
    setupAppointmentForm();
});

async function loadAppointments() {
    const params = currentStatusFilter ? `?status=${currentStatusFilter}` : '';
    const res = await fetch(`/api/appointments${params}`);
    appointments = await res.json();
    renderAppointmentsTable();
}

async function loadPetsForSelect() {
    const res = await fetch('/api/pets');
    petsForSelect = await res.json();
    renderPetOptions();
}

function renderPetOptions() {
    const select = document.getElementById('appointment-pet');
    select.innerHTML = '<option value="">Seleccionar mascota</option>';
    petsForSelect.forEach(pet => {
        select.innerHTML += `<option value="${pet._id}">${pet.name} (${pet.owner_name || pet.owner_phone})</option>`;
    });
}

function renderAppointmentsTable() {
    const tbody = document.getElementById('appointments-table-body');

    if (appointments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-sm text-gray-500">No hay citas</td></tr>';
        return;
    }

    const statusStyles = {
        scheduled: 'bg-blue-100 text-blue-800',
        confirmed: 'bg-green-100 text-green-800',
        completed: 'bg-gray-100 text-gray-800',
        cancelled: 'bg-red-100 text-red-800',
    };

    const statusLabels = {
        scheduled: 'Programada',
        confirmed: 'Confirmada',
        completed: 'Completada',
        cancelled: 'Cancelada',
    };

    tbody.innerHTML = appointments.map(apt => {
        const date = apt.date ? new Date(apt.date).toLocaleString('es', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit',
        }) : '-';
        const petName = apt.pet?.name || 'Desconocida';
        const style = statusStyles[apt.status] || 'bg-gray-100 text-gray-800';
        const label = statusLabels[apt.status] || apt.status;

        return `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${date}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${petName}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${apt.reason}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${apt.veterinarian || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <select onchange="updateAppointmentStatus('${apt._id}', this.value)"
                            class="text-xs rounded-full px-2 py-1 font-medium ${style} border-0 cursor-pointer">
                        <option value="scheduled" ${apt.status === 'scheduled' ? 'selected' : ''}>Programada</option>
                        <option value="confirmed" ${apt.status === 'confirmed' ? 'selected' : ''}>Confirmada</option>
                        <option value="completed" ${apt.status === 'completed' ? 'selected' : ''}>Completada</option>
                        <option value="cancelled" ${apt.status === 'cancelled' ? 'selected' : ''}>Cancelada</option>
                    </select>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <button onclick="editAppointment('${apt._id}')" class="text-indigo-600 hover:text-indigo-900 mr-3">Editar</button>
                    <button onclick="deleteAppointment('${apt._id}')" class="text-red-600 hover:text-red-900">Eliminar</button>
                </td>
            </tr>
        `;
    }).join('');
}

function setupAppointmentForm() {
    document.getElementById('appointment-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const aptId = document.getElementById('appointment-id').value;
        const data = {
            pet_id: document.getElementById('appointment-pet').value,
            date: document.getElementById('appointment-date').value,
            reason: document.getElementById('appointment-reason').value,
            veterinarian: document.getElementById('appointment-vet').value,
        };

        const url = aptId ? `/api/appointments/${aptId}` : '/api/appointments';
        const method = aptId ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
        });

        if (res.ok) {
            closeAppointmentModal();
            loadAppointments();
        }
    });
}

function openAppointmentModal(aptId = null) {
    document.getElementById('appointment-modal').classList.remove('hidden');
    document.getElementById('appointment-modal-title').textContent = aptId ? 'Editar cita' : 'Nueva cita';
    document.getElementById('appointment-id').value = '';
    document.getElementById('appointment-form').reset();

    if (aptId) {
        const apt = appointments.find(a => a._id === aptId);
        if (apt) {
            document.getElementById('appointment-id').value = apt._id;
            document.getElementById('appointment-pet').value = apt.pet_id;
            document.getElementById('appointment-date').value = apt.date ? apt.date.slice(0, 16) : '';
            document.getElementById('appointment-reason').value = apt.reason;
            document.getElementById('appointment-vet').value = apt.veterinarian || '';
        }
    }
}

function closeAppointmentModal() {
    document.getElementById('appointment-modal').classList.add('hidden');
}

function editAppointment(aptId) {
    openAppointmentModal(aptId);
}

async function updateAppointmentStatus(aptId, status) {
    await fetch(`/api/appointments/${aptId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status}),
    });
    loadAppointments();
}

async function deleteAppointment(aptId) {
    if (!confirm('¿Estás seguro de eliminar esta cita?')) return;

    const res = await fetch(`/api/appointments/${aptId}`, {method: 'DELETE'});
    if (res.ok) {
        loadAppointments();
    }
}

function filterAppointments(status) {
    currentStatusFilter = status;

    document.querySelectorAll('.apt-filter').forEach(btn => {
        btn.classList.remove('active', 'bg-indigo-100', 'text-indigo-700');
        btn.classList.add('bg-gray-100', 'text-gray-600');
    });
    const activeBtn = document.querySelector(`.apt-filter[data-filter="${status}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active', 'bg-indigo-100', 'text-indigo-700');
        activeBtn.classList.remove('bg-gray-100', 'text-gray-600');
    }

    loadAppointments();
}
