"""
Regras de negócio (Service) para usuários.
"""

from dataclasses import dataclass
from typing import Dict
from pymongo.errors import DuplicateKeyError
from ..extensions import bcrypt
from ..repositories.user_repo import UserRepository  # ✅ importa o tipo direto do pacote repositories


@dataclass
class UserService:
    """Serviço de domínio para usuários.

    Mantém regras de negócio isoladas do controller e da persistência.
    """
    repo: UserRepository  # ✅ sem referência a `services.user_repo` (evita circularidade)

    def bootstrap_admin_if_empty(self, payload: Dict) -> Dict:
        """Cria o primeiro admin se não existir nenhum usuário."""
        if self.repo.count() == 0 and payload.get("perfil") == "admin":
            return self._create_user(payload)
        raise PermissionError("Bootstrap only allowed for first admin user.")

    def create_user(self, payload: Dict) -> Dict:
        """Cria um novo usuário (controller faz RBAC)."""
        return self._create_user(payload)

    def _create_user(self, payload: Dict) -> Dict:
        """Implementa criação: normaliza, faz hash e persiste."""
        doc = {
            "nome": payload["nome"],
            "email": payload["email"].lower(),
            "perfil": payload["perfil"],
            "senha_hash": bcrypt.generate_password_hash(payload["senha"]).decode("utf-8"),
            "ativo": True,
        }
        try:
            self.repo.insert(doc)
        except DuplicateKeyError:
            raise ValueError("E-mail já cadastrado.")

        created = self.repo.find_by_email(doc["email"])
        return self.repo.to_public(created)
