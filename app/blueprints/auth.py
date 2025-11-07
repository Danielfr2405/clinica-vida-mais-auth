"""
Controllers (Blueprint) do domínio de Autenticação/Usuários.

Princípios:
- Controller deve ser fino: valida entrada, chama service e formata saída.
- Reuso de schemas para validação/serialização.
- RBAC com decorator @roles_required para rotas sensíveis.
"""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from ..schemas.user_schema import RegisterSchema, PublicUserSchema
from ..services import user_service, user_repo
from ..utils.auth import roles_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.record
def _on_register(setup_state):
    """Hook executado quando o blueprint é registrado.

    Uso:
        - Criar índices da coleção `users` de forma idempotente.
    Observação:
        - O try/except evita falha dura se o Mongo estiver indisponível
          no import-time (útil em ambientes locais).
    """
    try:
        user_repo.ensure_indexes()
    except Exception:
        # Em logs de prod, ideal registrar o erro (logger.warning/exception)
        pass


@auth_bp.post("/register")
@roles_required("admin")  # Somente admin pode criar usuários
def register():
    """Cria um novo usuário (admin-only).

    Fluxo:
        1) Valida entrada via Marshmallow.
        2) Chama service.create_user (hash + persistência + projeção pública).
        3) Retorna usuário público com HTTP 201.

    Erros:
        - 400: payload inválido
        - 409: e-mail duplicado
    """
    schema = RegisterSchema()
    try:
        payload = schema.load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        user = user_service.create_user(payload)
    except ValueError as e:
        return jsonify({"message": str(e)}), 409

    return PublicUserSchema().dump(user), 201


@auth_bp.post("/register/bootstrap")
def bootstrap_admin():
    """Cria o primeiro admin quando não existe nenhum usuário.

    Segurança:
        - Rota não exige JWT, porém só funciona se a coleção estiver vazia
          e o perfil solicitado for "admin".
    """
    schema = RegisterSchema()
    try:
        payload = schema.load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        user = user_service.bootstrap_admin_if_empty(payload)
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
    except ValueError as e:
        return jsonify({"message": str(e)}), 409

    return PublicUserSchema().dump(user), 201


@auth_bp.post("/login")
def login():
    """Autentica usuário e emite tokens JWT (access + refresh).

    Entrada:
        { "email": str, "senha": str }

    Saída:
        {
          "access_token": str,
          "refresh_token": str,
          "token_type": "bearer"
        }

    Erros:
        - 401: credenciais inválidas
    """
    data = request.get_json(force=True)
    email = (data.get("email") or "").lower()
    senha = data.get("senha") or ""

    # Busca usuário por e-mail
    user = user_repo.find_by_email(email)
    if not user:
        return jsonify({"message": "Credenciais inválidas"}), 401

    # Valida senha com bcrypt
    from ..extensions import bcrypt
    if not bcrypt.check_password_hash(user["senha_hash"], senha):
        return jsonify({"message": "Credenciais inválidas"}), 401

    # Claims mínimas: perfil e email (podem ser expandidas conforme necessidade)
    claims = {"perfil": user["perfil"], "email": user["email"]}
    identity = str(user["_id"])  # subject do token

    return {
        "access_token": create_access_token(identity=identity, additional_claims=claims),
        "refresh_token": create_refresh_token(identity=identity, additional_claims=claims),
        "token_type": "bearer",
    }, 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Renova o access token usando um refresh token válido.

    Requer:
        Header: Authorization: Bearer <refresh_token>

    Retorna:
        200: { "access_token": "...", "token_type": "bearer" }
    """
    identity = get_jwt_identity()   # subject do usuário
    claims = get_jwt() or {}        # mantemos perfil/email do refresh
    new_access = create_access_token(
        identity=identity,
        additional_claims={
            "perfil": claims.get("perfil"),
            "email": claims.get("email"),
        },
    )
    return {"access_token": new_access, "token_type": "bearer"}, 200


@auth_bp.get("/me")
@jwt_required()
def me():
    """Retorna dados do usuário autenticado usando o subject do JWT."""
    from ..extensions import mongo
    from bson import ObjectId

    user_id = get_jwt_identity()
    doc = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not doc:
        return jsonify({"message": "Usuário não encontrado"}), 404

    return {
        "id": str(doc["_id"]),
        "nome": doc["nome"],
        "email": doc["email"],
        "perfil": doc["perfil"],
    }
