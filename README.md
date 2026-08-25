# Automatización de gestión de citas y WhatsApp — Clínica de Adolfo

## Contexto

Pablo es ingeniero industrial con experiencia construyendo automatizaciones (proyecto en marcha: **Prospector**, para corredurías de seguros). Este proyecto busca desarrollar una herramienta para una clínica cuya administrativa, **Carmen**, gestiona hoy manualmente:

- Las citas de los pacientes
- La comunicación por WhatsApp con los clientes (confirmaciones, recordatorios, dudas, reprogramaciones)

El dueño/decisor de la clínica es **Adolfo**. Carmen es el contacto interno de confianza — quien vive el problema día a día y quien puede validar si esto tiene sentido antes de proponérselo a Adolfo.

> **Principio no negociable del proyecto:** esta herramienta no está pensada para sustituir a Carmen ni para reducir su rol. Está pensada para quitarle el trabajo mecánico y repetitivo (recordatorios uno a uno, preguntas frecuentes, rellenar huecos de agenda) para que ella pueda dedicar su tiempo a lo que de verdad requiere criterio humano: pacientes con dudas complejas, incidencias, atención personalizada. Cualquier funcionalidad que se proponga debe reforzar el rol de Carmen como punto de control, no diluirlo. Este encuadre debe quedar reflejado en el producto: ella ve todo, decide las excepciones, el sistema nunca actúa a sus espaldas.

## Objetivo del proyecto

Automatizar la comunicación repetitiva por WhatsApp asociada a la gestión de citas, con el objetivo de:

1. Reducir el número de citas perdidas por no-shows (recordatorios automáticos)
2. Recuperar ingresos rellenando huecos de última hora por cancelación (lista de espera automática)
3. Reducir el volumen de mensajes manuales que Carmen tiene que escribir uno a uno (FAQ automatizadas)
4. Dar a Carmen y Adolfo visibilidad clara de lo que el sistema gestiona y lo que escala a un humano

## Usuarios del sistema

- **Carmen** (usuaria operativa diaria): necesita ver de un vistazo qué está pasando, intervenir cuando el sistema no puede resolver algo, y sentir que tiene el control, no que un bot ha ocupado su puesto.
- **Adolfo** (decisor/propietario): le interesan resultados de negocio — menos huecos vacíos en la agenda, menos tiempo administrativo, no la tecnología en sí.
- **Pacientes** (destinatarios indirectos): reciben mensajes de WhatsApp automáticos; deben poder responder con naturalidad y llegar a una persona real si lo necesitan.

## Principios de diseño

1. **Carmen primero.** Toda decisión de diseño se evalúa por si facilita el trabajo de Carmen o si la reemplaza. Lo segundo se descarta.
2. **Escalado claro a humano.** Cualquier mensaje que el sistema no pueda resolver con confianza debe pasar a Carmen de forma visible, nunca quedarse en un limbo automatizado.
3. **Empezar manual, automatizar después.** Antes de automatizar nada, validar con Carmen el volumen real (nº de citas/mes, % de no-shows, horas/semana dedicadas a WhatsApp) para dimensionar el problema de verdad.
4. **Complejidad invisible.** Carmen y Adolfo no deben tener que entender WhatsApp Business API, webhooks, ni scheduler. Ven una interfaz simple: agenda, estado de cada cita, mensajes pendientes de revisión.
5. **Dato clínico fuera de alcance por defecto.** El sistema gestiona logística de citas (fecha, hora, confirmación), no contenido clínico. Ver sección de protección de datos.

## Alcance funcional (MVP)

**Incluido:**

- Recordatorio automático de cita por WhatsApp (24-48h antes), con opción de confirmar/cancelar/reprogramar respondiendo al mensaje
- Cuando un paciente cancela, oferta automática del hueco liberado a la lista de espera (por orden de prioridad a definir)
- Respuestas automáticas a preguntas frecuentes predefinidas (horario, dirección, qué traer, precio orientativo si aplica)
- Panel para Carmen: agenda del día/semana, estado de cada cita (confirmada/pendiente/cancelada), bandeja de mensajes escalados que requieren respuesta humana
- Métricas simples para Adolfo: no-shows evitados, huecos recuperados, mensajes gestionados automáticamente vs. escalados a Carmen

**Explícitamente fuera de alcance (por ahora):**

- Cualquier triage médico o clasificación de motivo de consulta
- Procesamiento o almacenamiento de contenido clínico (síntomas, diagnósticos, tratamientos)
- Toma de decisiones sin supervisión de Carmen en casos ambiguos
- Integración con el sistema de gestión de citas actual de la clínica (a validar en fase 2, ver preguntas pendientes)

## Protección de datos (restricción de diseño, no opcional)

La clínica maneja datos de salud, categoría especial bajo RGPD. Aunque el sistema no debe procesar contenido clínico, el mero hecho de vincular nombre + teléfono + cita en una clínica ya requiere cuidado:

- Usar la API oficial de WhatsApp Business (Meta Cloud API o proveedor certificado tipo Twilio/360dialog) — nunca un número personal ni herramientas no autorizadas
- Minimización de datos: guardar solo lo estrictamente necesario para gestionar la cita (nombre, teléfono, fecha/hora, estado)
- Consentimiento explícito del paciente para recibir mensajes automatizados (esto debería articularse en el primer contacto o en el proceso de alta como paciente)
- Sin almacenamiento de motivo de consulta ni cualquier dato de salud en el sistema de mensajería

## Stack técnico recomendado

Mismo criterio que en Prospector — accesible sin herramientas que haya que aprender de cero a mitad de proyecto:

- **Backend:** Python
- **Frontend:** React o HTML/CSS/JS simple para empezar
- **Base de datos:** SQLite para el prototipo, migrable a PostgreSQL si escala
- **Mensajería:** WhatsApp Business API (Meta Cloud API directa, o Twilio/360dialog como intermediario si simplifica la integración)
- **Scheduler:** APScheduler o cron para los recordatorios automáticos
- **Herramienta de desarrollo:** Claude Code como copiloto principal

## Flujo técnico ejemplo (recordatorio + lista de espera)

```
Cita registrada en el sistema
  ↓
24-48h antes → envío automático de recordatorio por WhatsApp
  ↓
Paciente responde:
  - Confirma → estado actualizado, fin del flujo
  - Cancela → hueco liberado → oferta automática a lista de espera (por orden definido)
  - Pregunta algo no reconocido → escalado a bandeja de Carmen
  - No responde en X horas → segundo recordatorio o escalado a Carmen según regla configurada
```

## Cómo debe trabajar Claude Code en este proyecto

- Mantener lenguaje accesible — mentalidad técnica pero no programador profesional
- Antes de construir integraciones (con el sistema de citas actual de la clínica, con la API de WhatsApp), preguntar y confirmar en vez de asumir
- Priorizar siempre lo que reduce trabajo real a Carmen sobre lo técnicamente interesante
- Cualquier funcionalidad que pueda leerse como "sustituir a Carmen" debe señalarse explícitamente antes de construirse, no darse por hecho
- Construir primero un prototipo mínimo validable con datos ficticios, antes de tocar datos reales de pacientes

## Preguntas pendientes de validar con Carmen/Adolfo antes de construir

- [x] ¿Qué sistema usan hoy para gestionar citas (agenda física, Excel, software específico tipo Doctoralia/Clinicware)? ¿Se puede integrar o hay que sustituirlo?
      → **Clinic Cloud** (del grupo Doctoralia), con integración nativa bidireccional con Doctoralia. Buena noticia: Clinic Cloud ofrece conectores/API (usados hoy para contabilidad, TPV, laboratorios), así que en fase 2 es plausible integrarse directamente con la agenda real en vez de duplicarla — pendiente de confirmar el acceso/plan contratado y si incluye API para terceros.
- [x] ¿Tienen ya un número de WhatsApp Business, o hay que darlo de alta?
      → Probablemente no — creemos que es un número de teléfono normal, no verificado como WhatsApp Business (a confirmar con certeza). **Acción a lanzar pronto:** dar de alta un número de WhatsApp Business (Meta Cloud API o vía Twilio/360dialog) es paso obligatorio antes de cualquier automatización real (principio no negociable de protección de datos, ver más abajo) y puede tardar días en verificarse — conviene iniciarlo en paralelo al resto del proyecto.
- [x] Volumen real: ¿cuántas citas al mes? ¿Qué % aproximado de no-shows?
      → **Más de 200 citas/mes** (~10/día laborable). % de no-shows aún sin dato concreto. Con este volumen y la mitad de la jornada de Carmen en WhatsApp, el caso de negocio para automatizar recordatorios y FAQ es sólido.
- [x] ¿Cuántas horas a la semana dedica Carmen a WhatsApp con pacientes?
      → Aproximadamente la mitad de su jornada. Confirma que el problema tiene volumen real: justifica priorizar recordatorios y FAQ automatizadas.
- [x] ¿Hay lista de espera hoy en algún formato, o habría que crearla desde cero?
      → No existe en ningún formato. Habría que crearla desde cero (lista de pacientes interesados en adelantar cita, por especialidad/profesional).
- [x] ¿Qué tipo de clínica es exactamente (afecta a qué preguntas frecuentes son relevantes y al nivel de sensibilidad de los datos)?
      → Clínica de salud privada con varias especialidades médicas.

**Dato nuevo (no estaba en la lista original):** cada profesional de la clínica tiene sus propios tiempos de consulta y días de la semana en los que atiende. Carmen irá facilitando esta información poco a poco. Esto afecta directamente al modelo de datos: la agenda no es única, sino por profesional (horario, duración de consulta y disponibilidad propios), y las citas y recordatorios deben calcularse en función de ese calendario individual.

**Datos de contacto/horario — verificación desde la web (centromedicoveedor.es):**

Al inspeccionar la web (WordPress + Elementor, sin sistema de citas online — el formulario de contacto solo envía nombre/email/mensaje a Carmen/Adolfo) se detectó una discrepancia entre lo indexado en buscadores y el HTML real de la página de contacto:

- **Dirección:** C/ Cervantes, 9, 11001 Cádiz (confirmado como correcto en el HTML en vivo). *Ojo: los resultados de búsqueda daban otra distinta (C. Veedor, 12, 11003 Cádiz) — no usar esa.*
- **Horario:** Mañanas L-V 08:30-13:30. Tardes L-J 17:00-20:00. **Viernes no abre por la tarde** (confirmado por Pablo).
- **Contacto:** consultas@centromedicoveedor.es · Tel. 856 58 16 58 · WhatsApp (solo mensajes, no llamadas): 667868024
- La web tiene un bloque de "horario de verano" oculto en el código con fechas de 2025 sin actualizar — recordatorio de que el contenido publicado no siempre está al día, conviene que Carmen confirme cualquier dato antes de usarlo en las FAQ automatizadas.

**Estado (25/08/2026): las 6 preguntas originales están respondidas.** Quedan flecos menores por confirmar con Carmen (% de no-shows, acceso/API concreta de Clinic Cloud, si el WhatsApp es realmente personal o ya alguna variante Business) antes de diseñar la primera integración real. El siguiente paso natural es un prototipo mínimo con datos ficticios, o seguir recopilando los horarios por profesional que Carmen va a ir facilitando.

**Este documento es el punto de partida.** En cuanto Carmen confirme interés, la primera sesión de trabajo debería centrarse en responder las preguntas pendientes antes de escribir una sola línea de código.
