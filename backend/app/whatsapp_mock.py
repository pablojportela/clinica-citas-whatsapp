"""Simulador de envío de WhatsApp.

No hay todavía un número de WhatsApp Business real (ver docs/whatsapp-business.md).
Esta función solo registra en base de datos lo que se "habría" enviado, para poder
validar el flujo completo con datos ficticios. Sustituir por una llamada real a la
Cloud API (o al SDK del proveedor elegido) cuando el número esté verificado.
"""

from sqlalchemy.orm import Session

from . import models


def enviar_whatsapp(db: Session, paciente: models.Paciente, texto: str, tipo: str) -> models.MensajeEnviado:
    mensaje = models.MensajeEnviado(paciente_id=paciente.id, texto=texto, tipo=tipo)
    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)
    print(f"[WHATSAPP SIMULADO -> {paciente.telefono}] {texto}")
    return mensaje
