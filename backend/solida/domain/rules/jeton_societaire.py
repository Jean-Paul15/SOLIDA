import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta

DUREE_SESSION = timedelta(minutes=20)


def _signature(secret: str, payload: bytes) -> bytes:
    return hmac.new(secret.encode(), payload, hashlib.sha256).digest()


def generer_jeton(secret: str, societaire_id: str) -> str:
    """Jeton signé, sans état côté serveur (pas de table de session) : le contenu
    porte sa propre expiration, vérifiée à chaque appel."""
    expiration = (datetime.now(UTC) + DUREE_SESSION).timestamp()
    payload = json.dumps({"societaire_id": societaire_id, "exp": expiration}).encode()
    signature = _signature(secret, payload)
    return (
        base64.urlsafe_b64encode(payload).decode()
        + "."
        + base64.urlsafe_b64encode(signature).decode()
    )


def verifier_jeton(secret: str, jeton: str) -> str | None:
    """None si le jeton est absent, malformé, falsifié ou expiré."""
    try:
        payload_b64, signature_b64 = jeton.split(".", 1)
        payload = base64.urlsafe_b64decode(payload_b64)
        signature = base64.urlsafe_b64decode(signature_b64)
    except (ValueError, TypeError):
        return None

    if not hmac.compare_digest(signature, _signature(secret, payload)):
        return None

    donnees = json.loads(payload)
    if datetime.now(UTC).timestamp() > donnees["exp"]:
        return None
    societaire_id = donnees["societaire_id"]
    return societaire_id if isinstance(societaire_id, str) else None
