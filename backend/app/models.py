from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Profesional(Base):
    __tablename__ = "profesionales"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    especialidad = Column(String, nullable=False)
    dias_semana = Column(String, nullable=False)  # p.ej. "L,M,X,J,V"
    hora_inicio = Column(String, nullable=False)  # "09:00"
    hora_fin = Column(String, nullable=False)  # "13:00"
    duracion_consulta_min = Column(Integer, default=30)

    citas = relationship("Cita", back_populates="profesional")


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    consentimiento_whatsapp = Column(Boolean, default=True)

    citas = relationship("Cita", back_populates="paciente")


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    estado = Column(String, default="pendiente")  # pendiente/confirmada/cancelada/completada/no_show
    recordatorio_enviado = Column(Boolean, default=False)

    paciente = relationship("Paciente", back_populates="citas")
    profesional = relationship("Profesional", back_populates="citas")


class ListaEspera(Base):
    __tablename__ = "lista_espera"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    especialidad = Column(String, nullable=False)
    fecha_alta = Column(DateTime, default=datetime.utcnow)
    atendido = Column(Boolean, default=False)

    paciente = relationship("Paciente")


class MensajeEscalado(Base):
    """Bandeja de Carmen: mensajes que el sistema no ha podido resolver solo."""

    __tablename__ = "mensajes_escalados"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    texto = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    resuelto = Column(Boolean, default=False)

    paciente = relationship("Paciente")


class MensajeEnviado(Base):
    """Registro de mensajes automáticos. Hoy simulado (ver whatsapp_mock.py);
    se sustituye por llamadas reales a la Cloud API cuando exista número Business."""

    __tablename__ = "mensajes_enviados"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    texto = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # recordatorio / lista_espera / faq
    fecha = Column(DateTime, default=datetime.utcnow)

    paciente = relationship("Paciente")
