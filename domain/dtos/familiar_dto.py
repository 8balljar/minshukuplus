# domain/dtos/familiar_dto.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class FamiliarDTO:
    id: Optional[int]
    hospedado_id: int
    nombre: str
    edad: Optional[int]
    sexo: str
    relacion: Optional[str]

