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
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-10 text-sm text-slate-400">No hay citas</td></tr>';
        return;
    }

    const statusStyles = {
        scheduled: 'bg-blue-50 text-blue-700 border border-blue-100',
        confirmed: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
        completed: 'bg-slate-100 text-slate-600',
        cancelled: 'bg-red-50 text-red-700 border border-red-100',
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
        const style = statusStyles[apt.status] || 'bg-slate-100 text-slate-600';
        const label = statusLabels[apt.status] || apt.status;

        return `
            <tr>
                <td>
                    <span class="font-semibold text-slate-900">${date}</span>
                </td>
                <td>${petName}</td>
                <td class="max-w-xs truncate">${apt.reason}</td>
                <td>${apt.veterinarian || '<span class="text-slate-300">-</span>'}</td>
                <td>
                    <select onchange="updateAppointmentStatus('${apt._id}', this.value)"
                            class="badge cursor-pointer border-0 outline-none ${style}" style="font-size: 0.6875rem;">
                        <option value="scheduled" ${apt.status === 'scheduled' ? 'selected' : ''}>Programada</option>
                        <option value="confirmed" ${apt.status === 'confirmed' ? 'selected' : ''}>Confirmada</option>
                        <option value="completed" ${apt.status === 'completed' ? 'selected' : ''}>Completada</option>
                        <option value="cancelled" ${apt.status === 'cancelled' ? 'selected' : ''}>Cancelada</option>
                    </select>
                </td>
                <td class="text-right">
                    <button onclick="editAppointment('${apt._id}')" class="link-action mr-3">Editar</button>
                    <button onclick="deleteAppointment('${apt._id}')" class="text-sm font-medium text-slate-400 hover:text-red-600 transition-colors">Eliminar</button>
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
    if (!confirm('Estas seguro de eliminar esta cita?')) return;

    const res = await fetch(`/api/appointments/${aptId}`, {method: 'DELETE'});
    if (res.ok) {
        loadAppointments();
    }
}

function filterAppointments(status) {
    currentStatusFilter = status;

    document.querySelectorAll('.apt-filter').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`.apt-filter[data-filter="${status}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    loadAppointments();
}
