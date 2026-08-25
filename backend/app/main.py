from datetime import date, datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .whatsapp_mock import enviar_whatsapp

app = FastAPI(title="Clínica — Panel de citas y WhatsApp (prototipo)")


def _cita_a_dict(c: models.Cita) -> dict:
    return {
        "id": c.id,
        "paciente": c.paciente.nombre,
        "telefono": c.paciente.telefono,
        "profesional": c.profesional.nombre,
        "especialidad": c.profesional.especialidad,
        "fecha_hora": c.fecha_hora.isoformat(),
        "estado": c.estado,
        "recordatorio_enviado": c.recordatorio_enviado,
    }


@app.get("/api/agenda")
def agenda(fecha: str | None = None, db: Session = Depends(get_db)):
    dia = date.fromisoformat(fecha) if fecha else date.today()
    inicio = datetime.combine(dia, datetime.min.time())
    fin = inicio + timedelta(days=1)
    citas = (
        db.query(models.Cita)
        .filter(models.Cita.fecha_hora >= inicio, models.Cita.fecha_hora < fin)
        .order_by(models.Cita.fecha_hora)
        .all()
    )
    return [_cita_a_dict(c) for c in citas]


@app.get("/api/citas")
def listar_citas(estado: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Cita)
    if estado:
        query = query.filter(models.Cita.estado == estado)
    citas = query.order_by(models.Cita.fecha_hora).all()
    return [_cita_a_dict(c) for c in citas]


@app.post("/api/citas/{cita_id}/cancelar")
def cancelar_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.get(models.Cita, cita_id)
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = "cancelada"
    db.commit()

    candidato = (
        db.query(models.ListaEspera)
        .filter(
            models.ListaEspera.especialidad == cita.profesional.especialidad,
            models.ListaEspera.atendido.is_(False),
        )
        .order_by(models.ListaEspera.fecha_alta)
        .first()
    )

    oferta_enviada = False
    if candidato:
        texto = (
            f"Hola {candidato.paciente.nombre.split()[0]}, se ha liberado un hueco el "
            f"{cita.fecha_hora.strftime('%d/%m')} a las {cita.fecha_hora.strftime('%H:%M')} "
            f"con {cita.profesional.nombre}. Responda SÍ para reservarlo."
        )
        enviar_whatsapp(db, candidato.paciente, texto, "lista_espera")
        candidato.atendido = True
        db.commit()
        oferta_enviada = True

    return {"cita": _cita_a_dict(cita), "oferta_lista_espera_enviada": oferta_enviada}


@app.get("/api/lista-espera")
def lista_espera(db: Session = Depends(get_db)):
    items = db.query(models.ListaEspera).order_by(models.ListaEspera.fecha_alta).all()
    return [
        {
            "id": e.id,
            "paciente": e.paciente.nombre,
            "especialidad": e.especialidad,
            "fecha_alta": e.fecha_alta.isoformat(),
            "atendido": e.atendido,
        }
        for e in items
    ]


@app.get("/api/bandeja")
def bandeja(db: Session = Depends(get_db)):
    items = (
        db.query(models.MensajeEscalado)
        .filter(models.MensajeEscalado.resuelto.is_(False))
        .order_by(models.MensajeEscalado.fecha)
        .all()
    )
    return [
        {
            "id": m.id,
            "paciente": m.paciente.nombre,
            "telefono": m.paciente.telefono,
            "texto": m.texto,
            "fecha": m.fecha.isoformat(),
        }
        for m in items
    ]


@app.post("/api/bandeja/{mensaje_id}/resolver")
def resolver_mensaje(mensaje_id: int, db: Session = Depends(get_db)):
    mensaje = db.get(models.MensajeEscalado, mensaje_id)
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    mensaje.resuelto = True
    db.commit()
    return {"ok": True}


@app.get("/api/metricas")
def metricas(db: Session = Depends(get_db)):
    total_citas = db.query(models.Cita).count()
    no_shows = db.query(models.Cita).filter(models.Cita.estado == "no_show").count()
    canceladas = db.query(models.Cita).filter(models.Cita.estado == "cancelada").count()
    huecos_recuperados = db.query(models.ListaEspera).filter(models.ListaEspera.atendido.is_(True)).count()
    mensajes_automaticos = db.query(models.MensajeEnviado).count()
    mensajes_escalados_total = db.query(models.MensajeEscalado).count()
    mensajes_escalados_pendientes = (
        db.query(models.MensajeEscalado).filter(models.MensajeEscalado.resuelto.is_(False)).count()
    )
    return {
        "total_citas": total_citas,
        "no_shows": no_shows,
        "citas_canceladas": canceladas,
        "huecos_recuperados_lista_espera": huecos_recuperados,
        "mensajes_gestionados_automaticamente": mensajes_automaticos,
        "mensajes_escalados_total": mensajes_escalados_total,
        "mensajes_escalados_pendientes": mensajes_escalados_pendientes,
    }


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
