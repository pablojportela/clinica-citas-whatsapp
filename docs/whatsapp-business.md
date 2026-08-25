# WhatsApp Business — qué es, qué permite y cómo montarlo

Documento técnico de apoyo (para Pablo, no para Carmen/Adolfo) sobre cómo funciona la plataforma de WhatsApp Business y qué opciones hay para este proyecto. Investigado el 25/08/2026.

## 1. Solo existe una vía: Cloud API

Desde octubre de 2025, Meta descontinuó la versión "On-Premise". Hoy la única forma de automatizar WhatsApp de forma oficial es la **WhatsApp Business Platform (Cloud API)**, alojada por Meta. No hay alternativa "ligera": cualquier automatización pasa por verificar un número como WhatsApp Business y conectarlo a esta API.

## 2. Cómo funciona el envío de mensajes (esto condiciona el diseño)

- **Ventana de 24 horas:** si el paciente ha escrito en las últimas 24h, se le puede responder con texto libre, sin restricciones (esto cubre las respuestas a FAQ).
- **Fuera de esa ventana** (p. ej., un recordatorio que iniciamos nosotros, sin que el paciente haya escrito antes), el mensaje **tiene que ser una plantilla pre-aprobada por Meta**. Esto afecta directamente a los recordatorios de cita, que son mensajes que iniciamos nosotros.
- Las plantillas se dividen en 3 categorías: **utility** (recordatorios, confirmaciones — la que usaremos casi siempre), **marketing** y **authentication**.
- Facturación: desde julio 2025 es **por mensaje entregado**, no por "conversación abierta" como antes. El coste depende del país y la categoría de plantilla.

**Implicación práctica:** antes de lanzar el primer recordatorio automático hay que diseñar y mandar a aprobar las plantillas (texto fijo con variables tipo "Hola {{nombre}}, tiene cita el {{fecha}} a las {{hora}} con {{profesional}}. Responda CONFIRMAR, CANCELAR o REPROGRAMAR."). La aprobación de Meta puede tardar horas o días — otra cosa a lanzar pronto, no a última hora.

## 3. Política de IA de Meta (cambio reciente, 15 enero 2026) — nos afecta directamente

Meta prohibió los **chatbots de IA de propósito general** dentro de WhatsApp (tipo ChatGPT, Perplexity, asistentes conversacionales abiertos).

**Lo que sigue permitido, explícitamente:** bots estructurados para reservas, soporte, seguimiento de pedidos/citas y notificaciones. Es decir, **nuestro caso de uso encaja de lleno** en lo permitido — mientras el sistema se mantenga como flujo estructurado (recordatorio con botones de confirmar/cancelar/reprogramar, respuestas a una lista cerrada de FAQ) y no se convierta en un chat abierto tipo "pregúntame lo que quieras". Esto refuerza, por motivos ahora también regulatorios y no solo de diseño, el principio del README de escalar a Carmen cualquier cosa que no encaje en el guion predefinido.

## 4. Aplicaciones / funcionalidades relevantes para este proyecto

- **Mensajes de plantilla (utility):** recordatorio de cita, aviso de hueco liberado a lista de espera, confirmación de reprogramación.
- **Botones de respuesta rápida:** en vez de que el paciente escriba texto libre, puede pulsar "Confirmar" / "Cancelar" / "Reprogramar" — reduce ambigüedad y mensajes que necesitan interpretación.
- **Webhooks entrantes:** cualquier respuesta del paciente (texto, botón pulsado) llega a nuestro backend en tiempo real vía webhook — así es como el sistema sabe que hay que actualizar el estado de la cita o escalar a Carmen.
- **Perfil de empresa verificado:** nombre, foto, horario y descripción de la clínica visibles en el chat — aporta confianza al paciente.

## 5. Cómo conectar la API: opciones

Todas usan el mismo Cloud API de Meta por debajo — la diferencia es quién gestiona la infraestructura y qué cobra encima.

| Opción | Cómo funciona | Coste aproximado | Cuándo tiene sentido |
|---|---|---|---|
| **Meta Cloud API directa** | Nos conectamos nosotros mismos a la API de Meta (Business Manager, tokens, webhooks) | Sin cuota mensual fija; solo se paga la tarifa de Meta por mensaje | Si queremos control total y no importa dedicar tiempo técnico a la integración (verificación de negocio, gestión de tokens, etc.) |
| **360dialog** (BSP) | Intermediario que da acceso a la Cloud API con una capa de gestión | ~49 €/mes por número, **sin recargo** sobre la tarifa de Meta | Volumen medio-alto y previsible (nuestro caso: >200 citas/mes → varios cientos de mensajes/mes). Coste fijo y predecible. |
| **Twilio** | Intermediario similar, con su propio SDK | Tarifa de Meta + ~0,005 $ extra por mensaje, sin cuota fija | Volumen bajo o muy variable, cuando no interesa comprometerse a una cuota mensual |

**Recomendación inicial (a validar, no decidida):** dado el volumen ya confirmado (+200 citas/mes, con recordatorio + posibles confirmaciones/reprogramaciones por cita, probablemente 400-800 mensajes/mes), **360dialog** parece la opción con mejor relación coste/sencillez — cuota fija baja, sin sorpresas por mensaje, y sigue siendo la Cloud API oficial de Meta por debajo (mismo cumplimiento RGPD y mismas plantillas). Twilio compensaría solo si el volumen real resulta ser mucho más bajo de lo estimado.

## 6. Pasos para dar de alta el número (independientes del resto del proyecto)

1. Verificar la identidad de la clínica como negocio en Meta Business Manager (Adolfo, como titular, probablemente deba aportar documentación del negocio).
2. Decidir: ¿migrar el número actual (667868024, el que ya conocen los pacientes) a WhatsApp Business, o dar de alta uno nuevo? Migrar el existente es mejor para no confundir a los pacientes, pero significa que ese número deja de poder usarse desde la app normal de WhatsApp del móvil de Carmen durante la transición — a coordinar con ella.
3. Registrar el número en la Cloud API (directamente o vía 360dialog/Twilio).
4. Diseñar y enviar a aprobar las plantillas de mensaje (recordatorio, lista de espera, etc.).
5. Conectar el webhook de mensajes entrantes al backend.

Este proceso puede tardar días por la verificación de Meta — es la razón por la que el README lo marca como algo a lanzar en paralelo, cuanto antes.
