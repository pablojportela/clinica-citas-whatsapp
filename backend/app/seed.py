"""Genera datos ficticios para probar el prototipo.

Especialidades tomadas de las que ofrece públicamente la clínica (Alergología,
Cardiología, Fisioterapia, Medicina general, Enfermería dermoestética), pero los
profesionales, pacientes y citas son inventados. No usar nunca con datos reales
de pacientes (ver principio de protección de datos en el README).
"""

from datetime import datetime, timedelta

from .database import Base, SessionLocal, engine
from . import models
from .whatsapp_mock import enviar_whatsapp


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    profesionales = [
        models.Profesional(
            nombre="Dra. Elena Ruiz",
            especialidad="Alergología",
            dias_semana="L,X,V",
            hora_inicio="09:00",
            hora_fin="13:00",
            duracion_consulta_min=20,
        ),
        models.Profesional(
            nombre="Dr. Marcos Ibáñez",
            especialidad="Cardiología",
            dias_semana="M,J",
            hora_inicio="10:00",
            hora_fin="14:00",
            duracion_consulta_min=30,
        ),
        models.Profesional(
            nombre="Laura Gómez (fisioterapeuta)",
            especialidad="Fisioterapia",
            dias_semana="L,M,X,J,V",
            hora_inicio="16:00",
            hora_fin="20:00",
            duracion_consulta_min=45,
        ),
        models.Profesional(
            nombre="Dr. Antonio Salas",
            especialidad="Medicina general",
            dias_semana="L,M,X,J,V",
            hora_inicio="09:00",
            hora_fin="13:00",
            duracion_consulta_min=15,
        ),
        models.Profesional(
            nombre="Carmen Díaz (enfermera dermoestética)",
            especialidad="Enfermería dermoestética",
            dias_semana="M,J",
            hora_inicio="10:00",
            hora_fin="13:00",
            duracion_consulta_min=30,
        ),
    ]
    db.add_all(profesionales)
    db.commit()

    nombres_ficticios = [
        "Ana Torres", "Luis Medina", "Marta Suárez", "Javier Ponce", "Cristina Vidal",
        "Pedro Cano", "Isabel Reyes", "Diego Fuentes", "Sofía Nieto", "Raúl Ortega",
        "Beatriz Lara", "Hugo Campos",
    ]
    pacientes = [
        models.Paciente(nombre=nombre, telefono=f"+34 600 000 {100 + i:03d}", consentimiento_whatsapp=True)
        for i, nombre in enumerate(nombres_ficticios)
    ]
    db.add_all(pacientes)
    db.commit()

    hoy = datetime.now().replace(minute=0, second=0, microsecond=0)

    def cita(paciente_idx, profesional_idx, dias_offset, hora, estado, recordatorio_enviado=False):
        fecha = (hoy + timedelta(days=dias_offset)).replace(hour=hora)
        return models.Cita(
            paciente_id=pacientes[paciente_idx].id,
            profesional_id=profesionales[profesional_idx].id,
            fecha_hora=fecha,
            estado=estado,
            recordatorio_enviado=recordatorio_enviado,
        )

    citas = [
        cita(0, 3, 0, 9, "confirmada", True),
        cita(1, 3, 0, 10, "pendiente", True),
        cita(2, 0, 0, 11, "confirmada", True),
        cita(3, 2, 1, 17, "pendiente", True),
        cita(4, 1, 1, 10, "confirmada", True),
        cita(5, 3, 2, 9, "cancelada", True),
        cita(6, 4, 2, 11, "confirmada", True),
        cita(7, 2, -1, 17, "no_show", True),
        cita(8, 0, 3, 9, "confirmada", False),
        cita(9, 3, 4, 9, "pendiente", False),
    ]
    db.add_all(citas)
    db.commit()

    lista_espera = [
        models.ListaEspera(paciente_id=pacientes[10].id, especialidad="Medicina general"),
        models.ListaEspera(paciente_id=pacientes[11].id, especialidad="Fisioterapia"),
    ]
    db.add_all(lista_espera)
    db.commit()

    mensajes_escalados = [
        models.MensajeEscalado(
            paciente_id=pacientes[2].id,
            texto="Hola, ¿puedo llevar a mi hijo pequeño a la sala de espera o tiene que quedarse fuera?",
        ),
        models.MensajeEscalado(
            paciente_id=pacientes[6].id,
            texto="Necesito cambiar mi cita de la semana que viene pero a un profesional distinto, ¿es posible?",
        ),
    ]
    db.add_all(mensajes_escalados)
    db.commit()

    # Simula recordatorios ya enviados para las citas que los tienen marcados
    for c in citas:
        if c.recordatorio_enviado:
            paciente = next(p for p in pacientes if p.id == c.paciente_id)
            profesional = next(pr for pr in profesionales if pr.id == c.profesional_id)
            texto = (
                f"Hola {paciente.nombre.split()[0]}, le recordamos su cita con "
                f"{profesional.nombre} el {c.fecha_hora.strftime('%d/%m')} a las "
                f"{c.fecha_hora.strftime('%H:%M')}. Responda CONFIRMAR, CANCELAR o REPROGRAMAR."
            )
            enviar_whatsapp(db, paciente, texto, "recordatorio")

    db.close()
    print("Datos ficticios generados en clinica.db")


if __name__ == "__main__":
    seed()
