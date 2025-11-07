"""
Utilidades de autenticação/autorização.

Motivação do decorator:
- Evitar repetir em cada rota a verificação de JWT + checagem de perfil.
- Tornar claro (por anotação) o contrato de acesso, ex.: @roles_required("admin")
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def roles_required(*roles: str):
    """Decorator RBAC simples baseado em claim `perfil` do JWT.

    Args:
        *roles: Perfis aceitos (ex.: "admin", "medico").

    Returns:
        Callable: Função decorada que exige JWT válido e perfil autorizado.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Garante que o token está presente e é válido
            verify_jwt_in_request()
            claims = get_jwt() or {}
            perfil = claims.get("perfil")

            # Regra de autorização mínima (poderia ser expandida no futuro)
            if perfil not in roles:
                return jsonify({"message": "Acesso negado"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
