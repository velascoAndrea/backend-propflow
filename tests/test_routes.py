import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "PropFlow API funcionando"}

def test_search_empty_query():
    response = client.post("/api/search", json={"query": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_search_valid_query():
    with patch("app.routes.generar_sql") as mock_sql, \
         patch("app.routes.ejecutar_query") as mock_query:
        mock_sql.return_value = "SELECT * FROM propiedades LIMIT 50"
        mock_query.return_value = [
            {
                "id": 1,
                "titulo": "Casa zona 10",
                "descripcion": "Hermosa casa",
                "tipo": "casa",
                "precio": 250000.00,
                "habitaciones": 3,
                "banos": 2,
                "area_m2": 180.00,
                "ubicacion": "Zona 10",
                "fecha_publicacion": "2024-01-15"
            }
        ]
        response = client.post("/api/search", json={"query": "casas en zona 10"})
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert response.json()["resultados"][0]["tipo"] == "casa"

def test_search_sql_injection():
    with patch("app.routes.generar_sql") as mock_sql:
        mock_sql.return_value = "DROP TABLE propiedades"
        response = client.post("/api/search", json={"query": "drop table"})
        assert response.status_code == 400

def test_search_returns_sql_generado():
    with patch("app.routes.generar_sql") as mock_sql, \
         patch("app.routes.ejecutar_query") as mock_query:
        mock_sql.return_value = "SELECT * FROM propiedades WHERE tipo = 'casa' LIMIT 50"
        mock_query.return_value = []
        response = client.post("/api/search", json={"query": "casas"})
        assert "sql_generado" in response.json()
        assert "SELECT" in response.json()["sql_generado"]