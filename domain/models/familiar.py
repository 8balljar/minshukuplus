# domain/models/familiar.py
from datetime import datetime
from peewee import (
    Model, AutoField, CharField, IntegerField, ForeignKeyField, DateTimeField, Check
)
from core.db import db
from domain.models.hospedado import Hospedado

class BaseModel(Model):
    class Meta:
        database = db

class Familiar(BaseModel):
    id = AutoField()
    hospedado = ForeignKeyField(Hospedado, backref="familia", on_delete="CASCADE")
    nombre = CharField(max_length=180)
    edad = IntegerField(null=True, constraints=[Check("edad >= 0 AND edad <= 120")])
    sexo = CharField(max_length=16, default="Hombre")
    relacion = CharField(max_length=40, null=True)

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} — {self.relacion or ''}"
