# domain/repositories/hospedado_repo.py
from typing import List, Tuple
from domain.models.hospedado import Hospedado
from domain.dtos.hospedado_dto import HospedadoDTO
from peewee import fn

class HospedadoRepository:
    def get(self, id_: int) -> HospedadoDTO:
        h = Hospedado.get_by_id(id_)
        return HospedadoDTO(
            id=h.id, nombre_completo=h.nombre_completo, rut=h.rut,
            correo=h.correo, telefono=h.telefono, edad=h.edad, sexo=h.sexo
        )

    def create(self, dto: HospedadoDTO) -> int:
        h = Hospedado.create(
            nombre_completo=dto.nombre_completo,
            rut=dto.rut,
            correo=dto.correo,
            telefono=dto.telefono,
            edad=dto.edad,
            sexo=dto.sexo,
        )
        return h.id

    def update(self, dto: HospedadoDTO) -> None:
        h = Hospedado.get_by_id(dto.id)
        h.nombre_completo = dto.nombre_completo
        h.correo = dto.correo
        h.telefono = dto.telefono
        h.edad = dto.edad
        h.sexo = dto.sexo
        h.save()

    def delete(self, id_: int) -> None:
        Hospedado.get_by_id(id_).delete_instance()

    # ---- Listado helpers ----
    def list_rows(self) -> List[Tuple[int, str]]:
        rows = []
        for h in Hospedado.select().order_by(Hospedado.nombre_completo.asc()):
            rows.append((h.id, f"{h.nombre_completo} ({h.rut})"))
        return rows

    def search_list_rows(self, q: str) -> List[Tuple[int, str]]:
        q = q.strip()
        if not q:
            return self.list_rows()
        pattern = f"%{q}%"
        qs = (Hospedado
              .select()
              .where(
                  (Hospedado.nombre_completo.contains(q)) |
                  (Hospedado.rut.contains(q)) |
                  (Hospedado.correo.contains(q)) |
                  (Hospedado.telefono.contains(q))
              )
              .order_by(Hospedado.nombre_completo.asc()))
        return [(h.id, f"{h.nombre_completo} ({h.rut})") for h in qs]
