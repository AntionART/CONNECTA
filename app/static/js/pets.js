// Pets management
let pets = [];

document.addEventListener('DOMContentLoaded', () => {
    loadPets();
    setupPetForm();
});

async function loadPets() {
    const res = await fetch('/api/pets');
    pets = await res.json();
    renderPetsTable();
}

function renderPetsTable() {
    const tbody = document.getElementById('pets-table-body');

    if (pets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-10 text-sm text-slate-400">No hay mascotas registradas</td></tr>';
        return;
    }

    const speciesMap = {dog: 'Perro', cat: 'Gato', bird: 'Ave', rabbit: 'Conejo', other: 'Otro'};
    const speciesIcon = {dog: '🐕', cat: '🐈', bird: '🐦', rabbit: '🐇', other: '🐾'};

    tbody.innerHTML = pets.map(pet => `
        <tr>
            <td>
                <div class="flex items-center gap-2.5">
                    <span class="text-lg">${speciesIcon[pet.species] || '🐾'}</span>
                    <span class="font-semibold text-slate-900">${pet.name}</span>
                </div>
            </td>
            <td>${speciesMap[pet.species] || pet.species}</td>
            <td>${pet.breed || '<span class="text-slate-300">-</span>'}</td>
            <td>${pet.age_years ? pet.age_years + ' a' : '<span class="text-slate-300">-</span>'}</td>
            <td>${pet.weight_kg ? pet.weight_kg + ' kg' : '<span class="text-slate-300">-</span>'}</td>
            <td>${pet.owner_name || '<span class="text-slate-300">-</span>'}</td>
            <td><span class="font-mono text-xs">${pet.owner_phone}</span></td>
            <td class="text-right">
                <button onclick="editPet('${pet._id}')" class="link-action mr-3">Editar</button>
                <button onclick="deletePet('${pet._id}')" class="text-sm font-medium text-slate-400 hover:text-red-600 transition-colors">Eliminar</button>
            </td>
        </tr>
    `).join('');
}

function setupPetForm() {
    document.getElementById('pet-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const petId = document.getElementById('pet-id').value;
        const data = {
            name: document.getElementById('pet-name').value,
            species: document.getElementById('pet-species').value,
            breed: document.getElementById('pet-breed').value,
            age_years: parseFloat(document.getElementById('pet-age').value) || 0,
            weight_kg: parseFloat(document.getElementById('pet-weight').value) || 0,
            owner_name: document.getElementById('pet-owner-name').value,
            owner_phone: document.getElementById('pet-owner-phone').value,
        };

        const url = petId ? `/api/pets/${petId}` : '/api/pets';
        const method = petId ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
        });

        if (res.ok) {
            closePetModal();
            loadPets();
        }
    });
}

function openPetModal(petId = null) {
    document.getElementById('pet-modal').classList.remove('hidden');
    document.getElementById('pet-modal-title').textContent = petId ? 'Editar mascota' : 'Nueva mascota';
    document.getElementById('pet-id').value = '';
    document.getElementById('pet-form').reset();

    if (petId) {
        const pet = pets.find(p => p._id === petId);
        if (pet) {
            document.getElementById('pet-id').value = pet._id;
            document.getElementById('pet-name').value = pet.name;
            document.getElementById('pet-species').value = pet.species;
            document.getElementById('pet-breed').value = pet.breed || '';
            document.getElementById('pet-age').value = pet.age_years || '';
            document.getElementById('pet-weight').value = pet.weight_kg || '';
            document.getElementById('pet-owner-name').value = pet.owner_name || '';
            document.getElementById('pet-owner-phone').value = pet.owner_phone;
        }
    }
}

function closePetModal() {
    document.getElementById('pet-modal').classList.add('hidden');
}

function editPet(petId) {
    openPetModal(petId);
}

async function deletePet(petId) {
    if (!confirm('Estas seguro de eliminar esta mascota?')) return;

    const res = await fetch(`/api/pets/${petId}`, {method: 'DELETE'});
    if (res.ok) {
        loadPets();
    }
}
