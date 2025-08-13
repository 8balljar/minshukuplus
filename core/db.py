# core/db.py
from __future__ import annotations
from pathlib import Path
from datetime import datetime
from peewee import (
    Model, SqliteDatabase, AutoField, CharField, IntegerField, BooleanField,
    DateTimeField, ForeignKeyField, TextField, Check
)

# -------------------------------------------------------------------
# Config DB (SQLite en data/minshuku.sqlite)
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # asegura la carpeta

DB_PATH = DATA_DIR / "minshuku.sqlite"
db = SqliteDatabase(
    str(DB_PATH),
    pragmas={
        "journal_mode": "wal",
        "foreign_keys": 1,
        "cache_size": -64 * 1024,  # ~64MB
    },
)

# -------------------------------------------------------------------
# BaseModel con timestamps
# -------------------------------------------------------------------
class BaseModel(Model):
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        database = db


# -------------------------------------------------------------------
# Tablas
# -------------------------------------------------------------------
class Anfitrion(BaseModel):
    id = AutoField()
    nombre_completo = CharField(max_length=180)
    rut = CharField(max_length=20, unique=True, index=True)
    telefono = CharField(max_length=32, null=True)
    correo = CharField(max_length=180, null=True)
    sexo = CharField(max_length=16, default="Hombre")          # validación real en servicio
    estado_civil = CharField(max_length=32, null=True)         # p.ej. "Casado", "Soltero"
    vinculo_casa = CharField(max_length=64, null=True)         # p.ej. "Propietario", "Arrendatario"

    def __str__(self) -> str:
        return f"{self.nombre_completo} ({self.rut})"


class Casa(BaseModel):
    id = AutoField()
    direccion = CharField(max_length=240)
    anfitrion = ForeignKeyField(Anfitrion, backref="casas", on_delete="CASCADE")

    # baños comunes de la casa
    banos_comunes = IntegerField(default=0, constraints=[Check("banos_comunes >= 0")])

    # totales de camas por tipo en la casa (si no manejas por pieza)
    camas_individual = IntegerField(default=0, constraints=[Check("camas_individual >= 0")])
    camas_matrimonial = IntegerField(default=0, constraints=[Check("camas_matrimonial >= 0")])
    camas_literas = IntegerField(default=0, constraints=[Check("camas_literas >= 0")])

    notas = TextField(null=True)

    def __str__(self) -> str:
        return f"{self.direccion} — {self.anfitrion.nombre_completo}"


class Pieza(BaseModel):
    id = AutoField()
    casa = ForeignKeyField(Casa, backref="piezas", on_delete="CASCADE")
    nombre = CharField(max_length=80)                           # p.ej. "Pieza 1", "Matrimonial"
    bano_privado = BooleanField(default=False)
    bano_detalle = CharField(max_length=120, null=True)

    camas_individual = IntegerField(default=0, constraints=[Check("camas_individual >= 0")])
    camas_matrimonial = IntegerField(default=0, constraints=[Check("camas_matrimonial >= 0")])
    camas_literas = IntegerField(default=0, constraints=[Check("camas_literas >= 0")])

    notas = TextField(null=True)

    def __str__(self) -> str:
        return f"{self.nombre} @ {self.casa.direccion}"


class Hospedado(BaseModel):
    id = AutoField()
    nombre_completo = CharField(max_length=180)
    rut = CharField(max_length=20, unique=True, index=True)
    correo = CharField(max_length=180, null=True)
    telefono = CharField(max_length=32, null=True)
    edad = IntegerField(null=True, constraints=[Check("edad >= 0 AND edad <= 120")])
    sexo = CharField(max_length=16, default="Hombre")
    viene_con_familia = BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.nombre_completo} ({self.rut})"


class Familiar(BaseModel):
    id = AutoField()
    hospedado = ForeignKeyField(Hospedado, backref="familia", on_delete="CASCADE")
    nombre = CharField(max_length=180)
    edad = IntegerField(null=True, constraints=[Check("edad >= 0 AND edad <= 120")])
    sexo = CharField(max_length=16, default="Hombre")
    relacion = CharField(max_length=40, null=True)             # "Cónyuge", "Hijo/a", etc.

    def __str__(self) -> str:
        return f"{self.nombre} — {self.relacion or ''}"


class Asignacion(BaseModel):
    """
    Asigna un hospedado a una casa y, opcionalmente, a una pieza específica.
    """
    id = AutoField()
    hospedado = ForeignKeyField(Hospedado, backref="asignaciones", on_delete="CASCADE")
    casa = ForeignKeyField(Casa, backref="asignaciones", on_delete="CASCADE")
    pieza = ForeignKeyField(Pieza, null=True, backref="asignaciones", on_delete="SET NULL")

    fecha_inicio = DateTimeField(default=datetime.now)
    fecha_fin = DateTimeField(null=True)                       # null = abierta
    estado = CharField(max_length=20, default="pendiente")     # "pendiente","activa","finalizada"
    notas = TextField(null=True)

    def __str__(self) -> str:
        return f"{self.hospedado.nombre_completo} → {self.casa.direccion}"


# -------------------------------------------------------------------
# Init / Close
# -------------------------------------------------------------------
ALL_MODELS = [Anfitrion, Casa, Pieza, Hospedado, Familiar, Asignacion]

def init_db(create_tables: bool = True) -> None:
    """
    Conecta y crea tablas si no existen. Llama a esto al inicio de la app.
    """
    db.connect(reuse_if_open=True)
    if create_tables:
        db.create_tables(ALL_MODELS, safe=True)

def close_db() -> None:
    if not db.is_closed():
        db.close()

# -------------------------------------------------------------------
# Inicialización automática al importar (opcional)
# -------------------------------------------------------------------
try:
    # Si prefieres control manual, comenta la línea siguiente y llama init_db() desde tu main.
    init_db(create_tables=True)
except Exception as _e:
    print(f"[db] Aviso: no se pudo inicializar DB en {DB_PATH}: {_e}")

# -------------------------------------------------------------------
# Alias de compatibilidad (código legado)
# -------------------------------------------------------------------
anfitrion = Anfitrion  # permite: from core.db import anfitrion
