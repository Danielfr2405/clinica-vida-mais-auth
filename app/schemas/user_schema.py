"""
Schemas de validação/serialização com Marshmallow.

Separar schemas:
- Mantém endpoints enxutos (controllers não reimplementam validação).
- Permite reuso e evoluções de contrato de API sem quebrar serviços.
"""

from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    """Entrada para criar usuário.

    Campos:
        nome (str): 2 a 100 caracteres.
        email (email): formato válido; normalizado para lowercase em service.
        senha (str): min 8; nunca devolvida (load_only).
        perfil (str): "admin" | "medico" | "recepcao".
    """
    nome = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    senha = fields.String(required=True, load_only=True, validate=validate.Length(min=8))
    perfil = fields.String(
        required=True, validate=validate.OneOf(["admin", "medico", "recepcao"])
    )


class PublicUserSchema(Schema):
    """Saída pública de usuário (sem hash de senha)."""
    id = fields.String()
    nome = fields.String()
    email = fields.Email()
    perfil = fields.String()
