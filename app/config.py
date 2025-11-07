"""
Configurações da aplicação via variáveis de ambiente.

Decisões:
- Evitamos .env para reduzir acoplamento; infraestrutura injeta as variáveis.
- JWT timeouts configuráveis para ajustes de segurança/usabilidade.
"""

import os
from datetime import timedelta


class Config:
    """Objeto de configuração do Flask.

    Variáveis suportadas (com defaults razoáveis para dev):
        - MONGO_URI (str): URI do MongoDB (ex.: mongodb://localhost:27017)
        - MONGO_DB_NAME (str): Nome do database (default: vida_mais)
        - SECRET_KEY (str): Chave do Flask (sessions/csrf)
        - JWT_SECRET_KEY (str): Chave para assinar JWT
        - JWT_ACCESS_MIN (int): Minutos de expiração do access token (default: 15)
        - JWT_REFRESH_DAYS (int): Dias de expiração do refresh token (default: 7)
    """

    def __init__(self) -> None:
        # Em produção, essas variáveis devem vir do ambiente/secret manager
        self.MONGO_URI = os.environ.get("MONGO_URI", "mongodb://master_user:240597@localhost:27017/gestao-clinica-vida-mais-cluster?authSource=admin")
        self.MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "gestao-clinica-vida-mais-cluster")
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
        self.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")

        # Timeouts JWT ajustáveis por env para facilitar tuning
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(
            minutes=int(os.environ.get("JWT_ACCESS_MIN", 15))
        )
        self.JWT_REFRESH_TOKEN_EXPIRES = timedelta(
            days=int(os.environ.get("JWT_REFRESH_DAYS", 7))
        )

        # JSON ordenado pode atrapalhar depuração; mantemos como False
        self.JSON_SORT_KEYS = False

        print('URI', self.MONGO_URI)
        print('DB', self.MONGO_DB_NAME)
        print('SECRET', self.SECRET_KEY)
        print('JWT', self.JWT_SECRET_KEY)
        print('JWT_ACCESS_TOKEN', self.JWT_ACCESS_TOKEN_EXPIRES)
        print('JWT_REFRESH', self.JWT_REFRESH_TOKEN_EXPIRES)
        print('JSON SORT_KEYS', self.JSON_SORT_KEYS)
