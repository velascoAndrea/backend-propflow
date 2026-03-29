# PropFlow — Backend

API REST construida con FastAPI que recibe búsquedas en lenguaje natural, las traduce a SQL usando un LLM local (Ollama) y retorna propiedades inmobiliarias desde MySQL.

## Stack Tecnológico

- **Python 3.11** + **FastAPI** — API REST con documentación automática
- **MySQL 8** — Base de datos relacional
- **Ollama** (llama3.2:3b) — LLM local para traducción de lenguaje natural a SQL
- **Docker + Docker Compose** — Orquestación de contenedores
- **pytest** — Pruebas unitarias

## Arquitectura

El flujo completo de una búsqueda es:
```
Usuario escribe consulta
        ↓
FastAPI recibe POST /api/search
        ↓
llm_service.py envía prompt a Ollama
        ↓
Ollama genera SQL con llama3.2:3b
        ↓
routes.py valida y sanitiza el SQL
        ↓
models.py ejecuta el SQL en MySQL
        ↓
Se retornan resultados en JSON
```

## Estructura del Proyecto
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # Configuración FastAPI y CORS
│   ├── routes.py        # Endpoints y validación SQL
│   ├── models.py        # Conexión y queries MySQL
│   └── llm_service.py  # Integración con Ollama
├── persistencia/
│   ├── schema.sql       # Creación de tabla propiedades
│   └── seed_data.sql    # 20 propiedades de ejemplo
├── tests/
│   └── test_routes.py   # 5 pruebas unitarias con pytest
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/search` | Búsqueda en lenguaje natural |
| GET | `/api/propiedades` | Lista todas las propiedades |

### Ejemplo de request
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Casas con 3 habitaciones en zona 10"}'
```

### Ejemplo de response
```json
{
  "query_original": "Casas con 3 habitaciones en zona 10",
  "sql_generado": "SELECT * FROM propiedades WHERE tipo = 'casa' AND habitaciones = 3 AND ubicacion LIKE '%10%' LIMIT 50",
  "resultados": [...],
  "total": 1
}
```

## Documentación Interactiva

FastAPI genera documentación automática con Swagger UI. Con el servidor corriendo visita:

**http://localhost:8000/docs**

Desde ahí puedes probar todos los endpoints sin necesidad de Postman o curl.

## Instalación y Configuración

### Prerrequisitos

- Docker y Docker Compose instalados
- Ollama instalado ([ollama.ai](https://ollama.ai))
- Modelo llama3.2:3b descargado

### Paso 1 — Instalar Ollama y descargar modelo
```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3.2:3b

# Verificar instalación
ollama list
```

### Paso 2 — Configurar Ollama para Docker (Linux)

**Importante para Linux:** Ollama por defecto solo escucha en `localhost`, lo que hace que los contenedores Docker no puedan acceder a él. Debes iniciarlo con `OLLAMA_HOST=0.0.0.0`:
```bash
# Detener el servicio del sistema si está corriendo
sudo systemctl stop ollama
sudo pkill -f ollama
sleep 2

# Iniciar Ollama escuchando en todas las interfaces
OLLAMA_HOST=0.0.0.0 ollama serve &

# Verificar que responde
curl http://172.17.0.1:11434
# Debe responder: Ollama is running

# Verificar que el modelo está disponible
curl http://172.17.0.1:11434/api/tags
```

> En Mac/Windows esto no es necesario — usar `host.docker.internal` en el `docker-compose.yml`.

### Paso 3 — Variables de entorno

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

| Variable | Default | Descripción |
|----------|---------|-------------|
| DB_HOST | mysql | Host de MySQL |
| DB_USER | appuser | Usuario de MySQL |
| DB_PASSWORD | apppass | Contraseña de MySQL |
| DB_NAME | propiedades_db | Nombre de la base de datos |
| OLLAMA_URL | http://172.17.0.1:11434 | URL de Ollama (Linux) |

### Paso 4 — Levantar con Docker Compose
```bash
docker-compose up --build
```

Esto levanta tres contenedores:
- **mysql** — Base de datos con schema y datos precargados
- **backend** — API FastAPI en puerto 8000
- **frontend** — Vue.js en puerto 8080

Para correr en background:
```bash
docker-compose up --build -d
```

Para detener:
```bash
docker-compose down
```

Para detener y eliminar volúmenes (resetea la DB):
```bash
docker-compose down -v
```

### Paso 5 — Verificar que todo funciona
```bash
# Health check del backend
curl http://localhost:8000

# Probar una búsqueda
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "casas en zona 10"}'
```

## Pruebas Unitarias
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Correr pruebas
pytest tests/ -v
```

Las pruebas cubren:
- ✅ Health check del API
- ✅ Validación de query vacía
- ✅ Búsqueda válida con mock
- ✅ Protección contra SQL injection
- ✅ Respuesta incluye SQL generado

## Seguridad

- **Validación de SQL** — Solo permite consultas SELECT
- **Bloqueo de palabras peligrosas** — DROP, DELETE, INSERT, UPDATE, ALTER, CREATE, TRUNCATE
- **Forzado de SELECT \*** — Evita queries que omitan campos necesarios
- **Timeout en Ollama** — 60 segundos máximo por request
- **Limpieza de respuesta** — Extrae solo el SQL de la respuesta del LLM, descartando texto extra

## Decisiones Técnicas

**¿Por qué FastAPI sobre Flask?**
FastAPI genera documentación automática con Swagger, tiene validación de tipos con Pydantic y es más rápido gracias a su naturaleza asíncrona.

**¿Por qué llama3.2:3b sobre mistral:7b?**
El modelo de 3B parámetros es más ligero y responde más rápido. Para traducción de lenguaje natural a SQL con un schema pequeño es suficientemente preciso.

**¿Por qué limpiar el SQL del LLM?**
Los modelos pequeños a veces envuelven el SQL en bloques de código markdown o agregan explicaciones. La función `limpiar_sql()` extrae solo el SQL válido usando expresiones regulares.

**¿Por qué charset utf8mb4 en la conexión MySQL?**
MySQL 8 usa por defecto autenticación SHA256 que requiere el paquete `cryptography`. Además utf8mb4 garantiza soporte completo de caracteres especiales y tildes en español.

## Troubleshooting

**Error: Connection refused a Ollama**
```bash
# Verificar que Ollama está corriendo
curl http://172.17.0.1:11434
# Si no responde, reiniciar con:
sudo systemctl stop ollama && OLLAMA_HOST=0.0.0.0 ollama serve &
```

**Error: modelo no encontrado en /api/tags**
```bash
# El modelo se descargó en otra instancia de Ollama
# Detener todo y reiniciar
sudo pkill -f ollama
OLLAMA_HOST=0.0.0.0 ollama serve &
ollama pull llama3.2:3b
```

**La DB no tiene datos**
```bash
# Recrear volúmenes
docker-compose down -v
docker-compose up --build
```