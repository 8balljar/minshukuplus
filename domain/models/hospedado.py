# domain/models/hospedado.py
from datetime import datetime
from peewee import (
    Model, AutoField, CharField, IntegerField, DateTimeField, Check
)
from core.db import db  # asegúrate de tener core/db.py con la instancia "db"


class BaseModel(Model):
    class Meta:
        database = db


class Hospedado(BaseModel):
    id = AutoField()
    nombre_completo = CharField(max_length=180)
    rut = CharField(max_length=20, unique=True, index=True)  # guarda con puntos/guión o limpio, pero único
    correo = CharField(max_length=180, null=True)
    telefono = CharField(max_length=32, null=True)           # texto (prefijos, ceros, +56, etc.)
    edad = IntegerField(null=True, constraints=[Check("edad >= 0 AND edad <= 120")])
    sexo = CharField(max_length=16, default="Hombre")         # validación real en service

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"
