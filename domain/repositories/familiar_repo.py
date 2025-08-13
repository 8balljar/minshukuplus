# domain/repositories/familiar_repo.py
from typing import List
from domain.models.familiar import Familiar
from domain.dtos.familiar_dto import FamiliarDTO
from domain.models.hospedado import Hospedado

class FamiliarRepository:
    def list_for_hospedado(self, hospedado_id: int) -> List[FamiliarDTO]:
        qs = Familiar.select().where(Familiar.hospedado == hospedado_id).order_by(Familiar.nombre.asc())
        out: List[FamiliarDTO] = []
        for f in qs:
            out.append(FamiliarDTO(
                id=f.id, hospedado_id=f.hospedado.id, nombre=f.nombre,
                edad=f.edad, sexo=f.sexo, relacion=f.relacion
            ))
        return out

    def create(self, dto: FamiliarDTO) -> int:
        h = Hospedado.get_by_id(dto.hospedado_id)
        f = Familiar.create(
            hospedado=h,
            nombre=dto.nombre,
            edad=dto.edad,
            sexo=dto.sexo,
            relacion=dto.relacion
        )
        return f.id

    def delete(self, familiar_id: int) -> None:
        Familiar.get_by_id(familiar_id).delete_instance()
