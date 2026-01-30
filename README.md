# Task Manager API

API RESTful simples para gerenciamento de tarefas de um time (um mini "todo" com regras reais).  
Desenvolvida com **FastAPI**, **SQLAlchemy 2.x**, **MySQL** e autenticação via **JWT**.

## Tecnologias utilizadas

- **Backend**: FastAPI (Python 3.11+)
- **Banco de dados**: MySQL + SQLAlchemy (ORM) + Alembic (migrações)
- **Autenticação**: JWT (OAuth2 Password Flow)
- **Validação e serialização**: Pydantic v2
- **Segurança**: passlib (argon2) + python-jose
- **Gerenciamento de dependências**: Poetry
- **Outras**: pydantic-settings

## Funcionalidades principais

- Registro e login de usuários
- CRUD completo de tarefas (criar, listar, buscar por ID, atualizar parcial, deletar)
- Tarefas vinculadas ao usuário autenticado (owner_id)
- Validação de permissões (apenas o dono edita/deleta)
- Documentação automática (Swagger + ReDoc)

## Pré-requisitos

- Python 3.11+
- Poetry instalado (`pip install poetry`)
- MySQL rodando (local)

## Instalação e execução

1. Clone o repositório

```bash
git clone <url-do-seu-repo> <dir>
cd <dir>
```

2. Instale as dependências

```bash
poetry install
```

3. Crie o arquivo `.env` a partir do exemplo. Edite `.env` com suas credenciais do MySQL

```bash
cp .env.example .env
```

4. Crie o banco de dados (se não existir)

```bash
mysql -u root -e "CREATE DATABASE task_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

5. Aplique as migrações iniciais

```bash
poetry run alembic upgrade head
```

6. Rode a API

```bash
poetry run fastapi run src/main.py --reload
```

Acesse:

* Swagger: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

## Rotas principais

|Método|Rota|Descrição|Autenticação|
-------|----|---------|------------|
|POST|/auth/register|Registrar novo usuário|Não|
|POST|/auth/login|Login e obter JWT|Não|
|GET|/auth/me|Dados do usuário logado|Sim|
|POST|/tasks/|Criar nova tarefa|Sim|
|GET|/tasks/|Listar tarefas do usuário|Sim|
|GET|/tasks/{task_id}|Detalhes de uma tarefa|Sim|
|PATCH|/tasks/{task_id}|Atualizar tarefa (parcial)|Sim|
|DELETE|/tasks/{task_id}|Deletar tarefa|Sim|

## Testando autenticação (exemplo com curl)

```bash
# 1. Registrar usuário
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"greg","email":"greg@example.com","password":"senha123"}'

# 2. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=greg&password=senha123" | jq -r .access_token)

# 3. Acessar /me com o token
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```
