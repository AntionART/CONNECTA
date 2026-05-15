"""
Pet Model — Linked to Owners via Phone Number.

Pets represent the animals registered in the veterinary CRM. Each pet
is linked to its owner through the owner_phone field, which matches
the phone_number in the conversations collection.

[GUÍA 9 - ACTIVIDAD 1] Modelo OOP completo: __init__, from_db, to_dict,
__str__, __repr__. Atributos PII prefijados con _ para encapsulamiento.
"""

from app.extensions import mongo
from app.models.base import BaseModel
from datetime import datetime, timezone
from bson import ObjectId


class Pet(BaseModel):
    COLLECTION = 'pets'

    # [GUÍA 9 - ACTIVIDAD 1] Constructor explícito con todos los atributos de la entidad.
    # Los campos PII (datos del dueño) se prefijan con _ para encapsulamiento.
    def __init__(self, name: str, species: str, breed: str,
                 age_years: float, weight_kg: float,
                 owner_phone: str, owner_name: str = '',
                 id: str = None, created_at=None, updated_at=None):
        """
        Inicializa una mascota con sus atributos explícitos.
        owner_phone y owner_name son PII — se protegen con prefijo _.
        """
        # [GUÍA 9 - ACTIVIDAD 1] Atributos públicos de la entidad mascota
        self.id = id
        # [GUÍA 2 - ACTIVIDAD 1] Tipos explícitos: name/species/breed son str,
        # age_years/weight_kg son float para admitir valores decimales (ej: 0.5 años)
        self.name = name
        self.species = species
        self.breed = breed
        self.age_years = age_years       # float — ej: 0.5 = 6 meses
        self.weight_kg = weight_kg       # float — ej: 4.2 kg
        self.created_at = created_at
        self.updated_at = updated_at
        # [GUÍA 9 - ACTIVIDAD 1] Atributos sensibles (PII) con convención _atributo
        self._owner_phone = owner_phone  # PII — número WhatsApp del dueño
        self._owner_name = owner_name    # PII — nombre del dueño

    # [GUÍA 9 - ACTIVIDAD 1] from_db — puente entre documento MongoDB y objeto Python.
    # Permite que BaseModel.find_by_id() retorne Pet en lugar de dict crudo.
    @classmethod
    def from_db(cls, document: dict) -> 'Pet':
        """Construye una instancia Pet desde un documento MongoDB."""
        if document is None:
            return None
        return cls(
            id=str(document['_id']),
            name=document.get('name', ''),
            species=document.get('species', ''),
            breed=document.get('breed', ''),
            age_years=document.get('age_years', 0.0),
            weight_kg=document.get('weight_kg', 0.0),
            owner_phone=document.get('owner_phone', ''),
            owner_name=document.get('owner_name', ''),
            created_at=document.get('created_at'),
            updated_at=document.get('updated_at'),
        )

    # [GUÍA 9 - ACTIVIDAD 1] to_dict — serializa la instancia a dict JSON-serializable.
    # Reemplaza la llamada serialize_doc(raw_dict) en las rutas REST.
    def to_dict(self) -> dict:
        """Serializa la mascota a dict compatible con JSON y MongoDB."""
        return {
            '_id': self.id,
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'age_years': self.age_years,
            'weight_kg': self.weight_kg,
            # [GUÍA 9 - ACTIVIDAD 2] Accede a atributos privados vía self._atributo
            'owner_phone': self._owner_phone,
            'owner_name': self._owner_name,
            'created_at': (
                self.created_at.isoformat()
                if isinstance(self.created_at, datetime)
                else self.created_at
            ),
            'updated_at': (
                self.updated_at.isoformat()
                if isinstance(self.updated_at, datetime)
                else self.updated_at
            ),
        }

    # [GUÍA 9 - ACTIVIDAD 1] __str__ — representación legible del estado del objeto
    def __str__(self) -> str:
        return (
            f"Pet('{self.name}', {self.species}, "
            f"{self.age_years} años, {self.weight_kg} kg, "
            f"dueño: {self._owner_phone})"
        )

    # [GUÍA 9 - ACTIVIDAD 1] __repr__ — representación técnica para debugging
    def __repr__(self) -> str:
        return (
            f"Pet(id={self.id!r}, name={self.name!r}, "
            f"species={self.species!r})"
        )

    # [GUÍA 9 - ACTIVIDAD 2] @property con getter para owner_phone (atributo PII)
    @property
    def owner_phone(self) -> str:
        """Número WhatsApp del dueño — dato PII protegido."""
        return self._owner_phone

    # [GUÍA 9 - ACTIVIDAD 2] @setter valida el formato antes de asignar
    @owner_phone.setter
    def owner_phone(self, value: str):
        if not value or not isinstance(value, str):
            raise ValueError("owner_phone debe ser un string no vacío")
        self._owner_phone = value.strip()

    # [GUÍA 9 - ACTIVIDAD 2] @property con getter para owner_name (PII)
    @property
    def owner_name(self) -> str:
        return self._owner_name

    # [GUÍA 9 - ACTIVIDAD 2] @setter normaliza el nombre del dueño
    @owner_name.setter
    def owner_name(self, value: str):
        self._owner_name = value.strip() if value else ''

    # [GUÍA 9 - ACTIVIDAD 2] Método de instancia: verifica la propiedad del dueño.
    # Migra la comparación externa a un comportamiento del objeto.
    def pertenece_a(self, phone: str) -> bool:
        """
        Verifica si la mascota pertenece al dueño del teléfono dado.
        Encapsula la comparación de PII dentro del objeto.
        """
        return self._owner_phone == phone.strip()

    # --- Operaciones de BD (métodos estáticos que interactúan con MongoDB) ---

    # [GUÍA 2 - ACTIVIDAD 1] Variables con tipos explícitos en el documento MongoDB
    @staticmethod
    def create(name, species, breed, age_years, weight_kg,
               owner_phone, owner_name='') -> 'Pet':
        doc = {
            'name': name,            # str — nombre de la mascota
            'species': species,      # str — especie (Perro, Gato, etc.)
            'breed': breed,          # str — raza
            'age_years': age_years,  # float — edad en años (ej: 0.5 = 6 meses)
            'weight_kg': weight_kg,  # float — peso en kilogramos
            'owner_phone': owner_phone,
            'owner_name': owner_name,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        result = mongo.db[Pet.COLLECTION].insert_one(doc)
        doc['_id'] = result.inserted_id
        # [GUÍA 9 - ACTIVIDAD 3] Retorna instancia Pet en lugar de dict crudo
        return Pet.from_db(doc)

    # [GUÍA 2 - ACTIVIDAD 3] Lista como resultado de consulta — ahora lista de instancias
    @staticmethod
    def find_by_owner_phone(phone) -> list:
        docs = list(mongo.db[Pet.COLLECTION].find({'owner_phone': phone}))
        # [GUÍA 9 - ACTIVIDAD 3] from_db convierte cada dict en instancia Pet
        return [Pet.from_db(doc) for doc in docs]

    @staticmethod
    def list_all() -> list:
        docs = list(mongo.db[Pet.COLLECTION].find().sort('created_at', -1))
        # [GUÍA 9 - ACTIVIDAD 3] Lista de instancias Pet
        return [Pet.from_db(doc) for doc in docs]


def init_pet_indexes():
    mongo.db[Pet.COLLECTION].create_index('owner_phone')
    mongo.db[Pet.COLLECTION].create_index('species')
