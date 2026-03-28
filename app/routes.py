from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.llm_service import generar_sql
from app.models import ejecutar_query
import re

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

def validar_sql(sql: str) -> bool:
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith("SELECT"):
        return False
    palabras_peligrosas = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"]
    for palabra in palabras_peligrosas:
        if palabra in sql_upper:
            return False
    return True

def forzar_select_all(sql: str) -> str:
    # Si el SQL no trae todos los campos, lo reemplazamos
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith("SELECT *"):
        # Reemplaza SELECT ... FROM por SELECT * FROM
        sql = re.sub(r'SELECT\s+.+?\s+FROM', 'SELECT * FROM', sql, flags=re.IGNORECASE | re.DOTALL)
    return sql

@router.post("/search")
async def search(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        sql = generar_sql(request.query)
        sql = forzar_select_all(sql)
        if not validar_sql(sql):
            raise HTTPException(status_code=400, detail="Generated query is not valid or safe")
        resultados = ejecutar_query(sql)
        return {
            "query_original": request.query,
            "sql_generado": sql,
            "resultados": resultados,
            "total": len(resultados)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/propiedades")
async def get_propiedades():
    try:
        resultados = ejecutar_query("SELECT * FROM propiedades LIMIT 50")
        return {"resultados": resultados, "total": len(resultados)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))