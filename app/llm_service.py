import requests
import os
import re

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def limpiar_sql(texto: str) -> str:
    # Busca SQL entre bloques de código
    match = re.search(r'```sql\s*(.*?)\s*```', texto, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Busca cualquier SELECT en el texto
    match = re.search(r'(SELECT\s+.*?;?)\s*$', texto, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return texto.strip()

def generar_sql(query_usuario: str) -> str:
    prompt = f"""You are a MySQL SQL expert. Your only task is to convert natural language queries to valid SQL.

The table is called 'propiedades' with these fields:
- id (INT)
- titulo (VARCHAR)
- descripcion (TEXT)
- tipo (ENUM: 'casa', 'departamento', 'terreno', 'oficina')
- precio (DECIMAL)
- habitaciones (INT)
- banos (INT)
- area_m2 (DECIMAL)
- ubicacion (VARCHAR)
- fecha_publicacion (DATE)

Strict rules:
1. Respond ONLY with the SQL query, no explanations or additional text
2. Use ONLY SELECT statements
3. Always use SELECT * to retrieve all fields
4. Always include LIMIT 50 at the end
5. For ubicacion field use LIKE '%value%' instead of exact match
6. For tipo field use exact match with lowercase values
7. Synonym normalization for tipo field - always translate to the correct DB value:
   - 'apartment', 'apto', 'apartamento', 'depa' → 'departamento'
   - 'house', 'casa', 'vivienda', 'hogar' → 'casa'
   - 'land', 'lote', 'terreno', 'solar' → 'terreno'
   - 'office', 'local', 'oficina' → 'oficina'

User query: {query_usuario}

SQL:"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )
    response.raise_for_status()
    sql_raw = response.json()["response"]
    sql = limpiar_sql(sql_raw)
    return sql