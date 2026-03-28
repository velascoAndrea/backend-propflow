# PropFlow — Backend

API REST construida con FastAPI que recibe búsquedas en lenguaje natural, las traduce a SQL usando Ollama y retorna propiedades inmobiliarias desde MySQL.

## Stack
- Python 3.11 + FastAPI
- MySQL 8
- Ollama (llama3.2:3b)
- Docker

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/search` | Búsqueda en lenguaje natural |
| GET | `/api/propiedades` | Lista todas las propiedades |

## Documentación interactiva
Con el servidor corriendo visita: http://localhost:8000/docs

## Instalación local

### Prerrequisitos
- Docker y Docker Compose
- Ollama corriendo con llama3.2:3b

### Levantar con Docker
```bash
# En Linux — iniciar Ollama primero
OLLAMA_HOST=0.0.0.0 ollama serve &

# Levantar servicios
docker-compose up --build
```

### Correr pruebas
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| DB_HOST | mysql | Host de MySQL |
| DB_USER | appuser | Usuario de MySQL |
| DB_PASSWORD | apppass | Contraseña de MySQL |
| DB_NAME | propiedades_db | Nombre de la base de datos |
| OLLAMA_URL | http://172.17.0.1:11434 | URL de Ollama |

## Seguridad
- Validación de SQL generado — solo permite SELECT
- Bloqueo de palabras peligrosas: DROP, DELETE, INSERT, UPDATE, ALTER
- Forzado de SELECT * para evitar queries incompletas