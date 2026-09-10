"""Valores permitidos (referencia, no rígidos).

Se guardan como texto en la BD para mantener flexibilidad (evitar enums rígidos
difíciles de modificar). Estas tuplas documentan el conjunto esperado y se pueden
usar para validación a nivel de aplicación.
"""

# Estado del negocio
BUSINESS_STATUS = ("activo", "cerrado_temporal", "cerrado_permanente", "desconocido")

# Estado de la vacante
JOB_STATUS = ("activa", "posible", "vencida", "eliminada", "desconocido")

# Alcance de la vacante (a qué sucursal/entidad corresponde)
JOB_SCOPE = ("sucursal", "corporativa", "ciudad_desconocida", "desconocido")

# Tipos de contacto
CONTACT_TYPES = (
    "telefono", "whatsapp", "web", "email",
    "facebook", "instagram", "tiktok", "linkedin", "otro",
)

# Niveles de confianza de un dato
CONFIDENCE = ("confirmado", "probable", "inferido", "desconocido")

# Estrategia de escaneo geográfico
SCAN_STRATEGY = ("radius", "grid", "polygon")

# Decisión del proceso de deduplicación
MATCH_DECISION = ("auto_merge", "manual_review", "rejected")

# Etiqueta de fuente para datos ficticios de demostración
SOURCE_DEMO = "DEMO"
