# 🏥 Gestão Clínica Vida+ — Serviço de Autenticação

Sistema de autenticação e controle de acesso (JWT + RBAC) para a aplicação **Gestão Clínica Vida+**.  
Permite cadastro, login, renovação de token e controle de permissões por perfil de usuário (`admin`, `medico`, `recepcao`).

---

## 🚀 Funcionalidades Principais

- 🔒 Autenticação via **JWT (access e refresh tokens)**  
- 👤 Cadastro de usuários (admin, médico, recepção)  
- 🧩 **RBAC** — Controle de acesso baseado em papéis (`roles_required`)  
- 🔁 Renovação de token (`/auth/refresh`)  
- 🩺 Health check (`/health`)  
- 🧱 Arquitetura modular (Blueprint + Service + Repository)  
- 💾 Integração com MongoDB  

---

## 🏗️ Estrutura do Projeto

```
gestao-clinica-vida-mais-auth/
├─ app/
│  ├─ __init__.py              → Criação da app Flask e inicialização
│  ├─ config.py                → Configurações (envs, JWT, Mongo)
│  ├─ extensions.py            → Extensões Flask (JWT, Bcrypt, Mongo)
│  ├─ blueprints/
│  │   └─ auth.py              → Rotas de autenticação
│  ├─ repositories/
│  │   └─ user_repo.py         → Acesso à base Mongo
│  ├─ services/
│  │   ├─ __init__.py          → Instâncias de serviço
│  │   └─ user_service.py      → Regras de negócio (cadastro)
│  ├─ schemas/
│  │   └─ user_schema.py       → Validação (Marshmallow)
│  └─ utils/
│      └─ auth.py              → Decorators JWT + RBAC
├─ wsgi.py                     → Ponto de entrada WSGI
├─ requirements.txt
└─ README.md                   → Este arquivo
```

---

## ⚙️ Requisitos

- Python 3.10+  
- MongoDB 6.x ou superior  
- Virtualenv (recomendado)

---

## ⚡️ Instalação e Execução Local

### 1️⃣ Clone o projeto
```bash
git clone https://github.com/seuusuario/gestao-clinica-vida-mais-auth.git
cd gestao-clinica-vida-mais-auth
```

### 2️⃣ Crie e ative o ambiente virtual
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3️⃣ Instale as dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure as variáveis de ambiente

#### Exemplo no Windows PowerShell:
```powershell
$env:MONGO_URI="mongodb://master_user:240597@localhost:27017/gestao-clinica-vida-mais-cluster?authSource=admin"
$env:MONGO_DBNAME="gestao-clinica-vida-mais-cluster"
$env:SECRET_KEY="super-secret"
$env:JWT_SECRET_KEY="jwt-secret"
$env:JWT_ACCESS_MIN=15
$env:JWT_REFRESH_DAYS=7
```

#### Exemplo no Linux / Mac:
```bash
export MONGO_URI="mongodb://master_user:240597@localhost:27017/gestao-clinica-vida-mais-cluster?authSource=admin"
export MONGO_DBNAME="gestao-clinica-vida-mais-cluster"
export SECRET_KEY="super-secret"
export JWT_SECRET_KEY="jwt-secret"
export JWT_ACCESS_MIN=15
export JWT_REFRESH_DAYS=7
```

### 5️⃣ Inicie a aplicação
```bash
flask --app wsgi:app run --host 0.0.0.0 --port 8000
```

---

## 🧠 Arquitetura de Software

A aplicação segue princípios de **Clean Architecture** e **DDD simplificado**, com os seguintes padrões:

| Camada | Padrão | Responsabilidade | Arquivo |
|--------|---------|------------------|----------|
| Controller | **Blueprint Pattern** | Define endpoints HTTP | `blueprints/auth.py` |
| Service | **Service Layer** | Contém regras de negócio | `services/user_service.py` |
| Repository | **Repository Pattern** | Abstrai acesso ao MongoDB | `repositories/user_repo.py` |
| RBAC | **Decorator Pattern** | Restringe acesso por papel | `utils/auth.py` |
| Schema | **DTO Pattern** | Validação de dados | `schemas/user_schema.py` |

---

## 🔐 Perfis e Regras (RBAC)

| Perfil | Permissões |
|--------|-------------|
| **admin** | Cadastrar usuários, médicos, recepcionistas |
| **medico** | Acesso futuro a rotas de pacientes e exames |
| **recepcao** | Acesso futuro a rotas de agendamentos e atendimentos |

---

## 🔑 JWT — Tokens

- **Access Token:**  
  Curto prazo (ex.: 15 minutos).  
  Usado para autenticar requisições comuns (`@jwt_required()`).

- **Refresh Token:**  
  Longo prazo (ex.: 7 dias).  
  Usado apenas em `/auth/refresh` (`@jwt_required(refresh=True)`).

---

## 🧩 Endpoints da API

### **GET /health**
Verifica se o serviço está operacional.  
**Resposta:**  
```json
{ "status": "ok" }
```

---

### **POST /auth/register/bootstrap**
Cria o primeiro usuário **admin** (sem necessidade de token).  
Funciona **apenas quando o banco está vazio**.  
**Body:**
```json
{
  "nome": "Administrador",
  "email": "admin@vida.com",
  "senha": "SenhaForte@123",
  "perfil": "admin"
}
```

**Resposta 201:**
```json
{
  "id": "...",
  "nome": "Administrador",
  "email": "admin@vida.com",
  "perfil": "admin"
}
```

---

### **POST /auth/login**
Autentica usuário e gera tokens JWT.

**Body:**
```json
{
  "email": "admin@vida.com",
  "senha": "SenhaForte@123"
}
```

**Resposta 200:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

---

### **POST /auth/register**
Cria novo usuário (somente **admin** pode acessar).

**Header:**
```
Authorization: Bearer <access_token>
```

**Body:**
```json
{
  "nome": "Dr. João da Silva",
  "email": "joao@vida.com",
  "senha": "SenhaForte@321",
  "perfil": "medico"
}
```

**Resposta 201:**
```json
{
  "id": "...",
  "nome": "Dr. João da Silva",
  "email": "joao@vida.com",
  "perfil": "medico"
}
```

---

### **POST /auth/refresh**
Renova o **access token** usando um **refresh token** válido.

**Header:**
```
Authorization: Bearer <refresh_token>
```

**Resposta 200:**
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

---

### **GET /auth/me**
Retorna informações do usuário autenticado.

**Header:**
```
Authorization: Bearer <access_token>
```

**Resposta 200:**
```json
{
  "id": "...",
  "nome": "Administrador",
  "email": "admin@vida.com",
  "perfil": "admin"
}
```

---

## 🧾 Fluxo Completo de Autenticação

1️⃣ `/auth/register/bootstrap` → cria o primeiro admin  
2️⃣ `/auth/login` → obtém access + refresh tokens  
3️⃣ `/auth/register` → admin cria novos usuários  
4️⃣ `/auth/me` → consulta usuário autenticado  
5️⃣ `/auth/refresh` → renova access token expirado  

---

## 💬 Códigos de Resposta

| Código | Descrição |
|--------|------------|
| 200 | OK |
| 201 | Criado com sucesso |
| 400 | Erro de validação |
| 401 | Token ausente ou inválido |
| 403 | Acesso negado (RBAC) |
| 409 | Recurso duplicado |
| 500 | Erro interno |

---

## 🧰 Exemplo cURL — Renovar Token

```bash
curl -X POST http://localhost:8000/auth/refresh   -H "Authorization: Bearer <REFRESH_TOKEN>"   -H "Content-Type: application/json"
```

---

## 🧩 Docker (opcional)

**docker-compose.yml**
```yaml
version: '3.9'

services:
  api-auth:
    build: .
    ports:
      - "8000:8000"
    environment:
      MONGO_URI: mongodb://master_user:240597@mongo:27017/gestao-clinica-vida-mais-cluster?authSource=admin
      MONGO_DBNAME: gestao-clinica-vida-mais-cluster
      SECRET_KEY: super-secret
      JWT_SECRET_KEY: jwt-secret
    depends_on:
      - mongo

  mongo:
    image: mongo:6
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: master_user
      MONGO_INITDB_ROOT_PASSWORD: 240597
    ports:
      - "27017:27017"
```

**Build e execução:**
```bash
docker compose up --build
```

---

## 🧪 Testes (exemplo Pytest)
```bash
pytest -v --disable-warnings
```

---

## 🧱 Futuras Extensões

- 🧾 Auditoria de logs (criação/alteração de usuários)  
- 🔁 Revogação e rotação de tokens (blocklist)  
- 📦 Módulo de agendamentos (para médicos e recepção)  
- 🧠 Integração OAuth2 (Google ou corporativo)  

---

## 👨‍💻 Autor

**Daniel Fernandes Rodrigues**  
Tech Lead & Backend Developer  
🏗️ Projeto: *Gestão Clínica Vida+ (auth microservice)*  
