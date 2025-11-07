"""
Ponto único para instanciar extensões de terceiros.

Motivação:
- Evita import circular e facilita testes/mocks.
- Melhor isolamento para troca de implementações (ex.: DB ou Hash diferente).
"""

from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo

bcrypt = Bcrypt()
"""BCrypt para hashing de senhas; evita armazenar plaintext."""

jwt = JWTManager()
"""Gerenciador de JSON Web Tokens; lida com criação/validação de tokens."""

mongo = PyMongo()
"""Cliente Mongo integrado ao Flask; expõe `mongo.db` para coleções."""
