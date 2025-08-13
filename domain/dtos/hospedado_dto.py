# domain/dtos/hospedado_dto.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class HospedadoDTO:
    id: Optional[int]
    nombre_completo: str
    rut: str
    correo: Optional[str]
    telefono: Optional[str]
    edad: Optional[int]
    sexo: str
