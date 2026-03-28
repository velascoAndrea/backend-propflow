CREATE DATABASE IF NOT EXISTS propiedades_db;
USE propiedades_db;

CREATE TABLE IF NOT EXISTS propiedades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo ENUM('casa', 'departamento', 'terreno', 'oficina') NOT NULL,
    precio DECIMAL(12, 2) NOT NULL,
    habitaciones INT DEFAULT 0,
    banos INT DEFAULT 0,
    area_m2 DECIMAL(10, 2),
    ubicacion VARCHAR(255),
    fecha_publicacion DATE NOT NULL
);