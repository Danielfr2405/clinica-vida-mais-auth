"""
Inicialização da aplicação Flask.

Responsabilidades deste módulo:
- Construir o app Flask e carregar configurações.
- Inicializar extensões (Mongo, JWT, Bcrypt).
- Registrar blueprints (ex.: auth).
- Expor um endpoint de health-check (/health).
"""

from flask import Flask
from .config import Config
from .extensions import bcrypt, jwt, mongo
from .blueprints.auth import auth_bp


def create_app() -> Flask:
    """Cria e configura a aplicação Flask.

    Returns:
        Flask: Instância de aplicativo configurada e pronta para uso.
    """
    app = Flask(__name__)
    # Carrega as configs a partir de variáveis de ambiente (sem .env obrigatório)
    app.config.from_object(Config())

    # Inicialização de extensões — mantém dependências centralizadas
    bcrypt.init_app(app)
    jwt.init_app(app)
    mongo.init_app(app)

    # Registro dos endpoints do domínio de autenticação sob o prefixo /auth
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.get("/health")
    def health():
        """Endpoint simples para liveness/readiness checks de infraestrutura."""
        return {"status": "ok"}

    return app
