"""
Camada de acesso a dados (Repository).

Boas práticas:
- Isolar PyMongo/ORM da camada de serviço.
- Oferecer uma interface pequena e clara focada no domínio.
- Criar índices de forma idempotente no setup.
"""

from typing import Optional, Dict
from ..extensions import mongo


class UserRepository:
    """Acesso à coleção `users` do MongoDB."""

    @property
    def _col(self):
        """Retorna a coleção `users` já conectada via PyMongo."""
        return mongo.db.users

    def ensure_indexes(self) -> None:
        """Garante índices necessários.

        Índices:
            - email (unique): evita duplicidade por chave natural do usuário.
        """
        # create_index é idempotente; múltiplas chamadas não quebram
        self._col.create_index("email", unique=True)

    def find_by_email(self, email: str) -> Optional[Dict]:
        """Busca um usuário pelo e-mail normalizado (lowercase recomendado)."""
        return self._col.find_one({"email": email})

    def count(self) -> int:
        """Retorna o total aproximado de usuários (eficiente para checks)."""
        return self._col.estimated_document_count()

    def insert(self, doc: Dict) -> str:
        """Insere um documento de usuário.

        Args:
            doc: dicionário já normalizado e com `senha_hash`.

        Returns:
            str: ID do documento inserido em formato string.
        """
        res = self._col.insert_one(doc)
        return str(res.inserted_id)

    def to_public(self, doc: Dict) -> Dict:
        """Projeção segura do documento para resposta pública.

        Remove campos sensíveis como `senha_hash`.
        """
        return {
            "id": str(doc.get("_id")),
            "nome": doc.get("nome"),
            "email": doc.get("email"),
            "perfil": doc.get("perfil"),
        }
