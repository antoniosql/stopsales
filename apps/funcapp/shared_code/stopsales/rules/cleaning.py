import re

_SIGNATURE_PATTERNS = [
    r"(?is)\n--\s*\n.*$",        # common signature delimiter
    r"(?is)\n__+\n.*$",          # underscores
    r"(?is)\nEnviado desde mi.*$", # ES mobile
    r"(?is)\nSent from my.*$",     # EN mobile
]


def clean_email_body(body: str) -> str:
    """Limpia el body del correo (firmas, disclaimers típicos, etc.).

    En producción, se recomienda:
    - un pre-procesador por proveedor
    - normalización de espacios
    - eliminar 'quoted replies' cuando sea posible
    """
    text = body.strip()
    for pat in _SIGNATURE_PATTERNS:
        text = re.sub(pat, "", text)
    # compacta whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
