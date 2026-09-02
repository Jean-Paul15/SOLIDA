from solida.infrastructure.auth.cookie import (
    authentication_backend,
    cookie_transport,
    get_strategy,
)
from solida.infrastructure.auth.current_user import current_active_user
from solida.infrastructure.auth.dependencies import client_ip_address, require_role
from solida.infrastructure.auth.manager import (
    UserManager,
    get_user_manager,
    load_common_passwords,
    revoke_user_tokens,
)
from solida.infrastructure.auth.session import get_session

__all__ = [
    "UserManager",
    "authentication_backend",
    "client_ip_address",
    "cookie_transport",
    "current_active_user",
    "get_session",
    "get_strategy",
    "get_user_manager",
    "load_common_passwords",
    "require_role",
    "revoke_user_tokens",
]
