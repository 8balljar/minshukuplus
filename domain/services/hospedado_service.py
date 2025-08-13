# domain/services/hospedado_service.py
from domain.dtos.hospedado_dto import HospedadoDTO
from utils.validators import is_valid_rut, is_valid_email

class HospedadoService:
    def validate(self, dto: HospedadoDTO, check_rut=True, check_name=True) -> list[str]:
        errs = []
        if check_name and not dto.nombre_completo.strip():
            errs.append("El nombre es obligatorio.")
        if check_rut and not is_valid_rut(dto.rut):
            errs.append("RUT inválido.")
        if dto.correo and not is_valid_email(dto.correo):
            errs.append("Correo inválido.")
        if dto.edad is not None and not (0 <= dto.edad <= 120):
            errs.append("La edad debe estar entre 0 y 120.")
        if dto.sexo not in {"Hombre", "Mujer"}:
            errs.append("Sexo inválido.")
        return errs
