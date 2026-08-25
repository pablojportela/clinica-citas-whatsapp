# Flujo de reservas — mismo motor, distintos canales de entrada

Cómo debería funcionar el proceso cuando un paciente pide/cancela/reprograma una cita, sea desde WhatsApp o desde la web. Principio de diseño: **un único motor de reservas**, con adaptadores por canal — nunca lógica duplicada por sitio, para que Carmen vea siempre un estado consistente en su panel sin sincronizar nada a mano.

## 1. Punto de entrada (varía por canal)

- **WhatsApp:** el paciente escribe texto libre, o pulsa un botón (CONFIRMAR / CANCELAR / REPROGRAMAR) en respuesta a un recordatorio. Llega al backend vía webhook de la Cloud API (ver `docs/whatsapp-business.md`).
- **Web:** el paciente rellena el formulario de contacto actual (`centromedicoveedor.es/contacto/`). Hoy solo pide nombre/email/mensaje, sin teléfono — de momento seguiría gestionándose como aviso manual a Carmen. Si se añade el campo teléfono al formulario, ese número podría enganchar directamente al paciente al mismo flujo de WhatsApp del punto 3, unificando ambos canales desde ahí.
- **Panel de Carmen:** ella también puede crear/cancelar una cita manualmente — usa el mismo motor por debajo (ya implementado así en el prototipo: `POST /api/citas/{id}/cancelar`).

## 2. Interpretación del mensaje (solo aplica a WhatsApp) — conservador, no ambicioso

- **Respuesta estructurada a un botón** (CONFIRMAR/CANCELAR/REPROGRAMAR) → acción directa, sin ambigüedad, se ejecuta sola.
- **Texto libre pidiendo cita nueva** ("quiero cita con el fisio") → se identifica la especialidad mencionada, se consulta el calendario propio de ese profesional (cada uno con sus días/horas — ver README) y se ofrecen los 2-3 próximos huecos libres; el paciente elige respondiendo un número.
- **Cualquier otra cosa** (pregunta ambigua, queja, algo que suene a clínico) → se escala directo a la bandeja de Carmen, sin intentar adivinar la respuesta.

Esta regla de "si no está claro, se escala" no es solo el principio de diseño del README — desde enero de 2026 es también un requisito de la política de Meta: los bots de WhatsApp deben ser flujos estructurados (reservas, notificaciones), no chatbots abiertos que improvisen respuestas.

## 3. Ejecución

Se crea/cancela/reprograma la cita a través de las mismas funciones internas, sea cual sea el canal que las disparó. Hoy escriben en nuestra base de datos (SQLite del prototipo); en producción escribirían también en Clinic Cloud vía su API, si el plan contratado lo permite, para que no existan dos agendas que se puedan desincronizar.

## 4. Confirmación al paciente

Por WhatsApp — plantilla pre-aprobada si han pasado más de 24h desde su último mensaje, o mensaje de sesión libre si están dentro de esa ventana.

## 5. El panel de Carmen se actualiza solo

No hay paso de sincronización manual: el panel lee siempre del mismo origen de datos que actualizan los otros canales. Ya está probado en el prototipo — `cancelar_cita()` cambia el estado y ofrece el hueco a la lista de espera, y da igual si se dispara desde el panel o desde una respuesta de WhatsApp: es la misma función.

## Antes de construir esta parte

Validar en persona con Carmen (o con vídeos/capturas suyos) cómo gestiona hoy estos mismos casos en Clinic Cloud y WhatsApp — qué información necesita para decidir un hueco, qué preguntas le hacen los pacientes con más frecuencia, dónde se atasca. Eso debe guiar qué se automatiza primero, no al revés.
