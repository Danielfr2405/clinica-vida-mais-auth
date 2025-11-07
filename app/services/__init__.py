"""
Service locator simples para instâncias do domínio.

Expõe:
- user_repo: repositório de usuários
- user_service: regras de negócio de usuário
"""

from ..repositories.user_repo import UserRepository
from .user_service import UserService

# Instâncias únicas usadas pelos controllers (evita acoplamento direto ao DB)
user_repo = UserRepository()
user_service = UserService(repo=user_repo)

__all__ = ["user_repo", "user_service", "UserService"]
