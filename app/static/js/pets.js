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
        tbody.innerHTML = '<tr><td colspan="8" class="px-6 py-8 text-center text-sm text-gray-500">No hay mascotas registradas</td></tr>';
        return;
    }

    const speciesMap = {dog: 'Perro', cat: 'Gato', bird: 'Ave', rabbit: 'Conejo', other: 'Otro'};

    tbody.innerHTML = pets.map(pet => `
        <tr>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${pet.name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${speciesMap[pet.species] || pet.species}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pet.breed || '-'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pet.age_years ? pet.age_years + ' años' : '-'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pet.weight_kg ? pet.weight_kg + ' kg' : '-'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pet.owner_name || '-'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pet.owner_phone}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button onclick="editPet('${pet._id}')" class="text-indigo-600 hover:text-indigo-900 mr-3">Editar</button>
                <button onclick="deletePet('${pet._id}')" class="text-red-600 hover:text-red-900">Eliminar</button>
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
    if (!confirm('¿Estás seguro de eliminar esta mascota?')) return;

    const res = await fetch(`/api/pets/${petId}`, {method: 'DELETE'});
    if (res.ok) {
        loadPets();
    }
}
