-- Script para crear/verificar la tabla codigos_cups con restricción UNIQUE
-- Ejecutar este script en pgAdmin o psql antes de usar el sistema de carga

-- Crear la tabla si no existe
CREATE TABLE IF NOT EXISTS codigos_cups (
    id SERIAL PRIMARY KEY,
    codigo_cups VARCHAR(20) NOT NULL,
    nombre_estudio VARCHAR,
    preparacion_especial BOOLEAN DEFAULT FALSE,
    remitido BOOLEAN DEFAULT FALSE,
    CONSTRAINT codigos_cups_codigo_unique UNIQUE (codigo_cups)
);

-- Si la tabla ya existe pero no tiene la restricción UNIQUE, agregarla
-- (Descomentar las siguientes líneas si es necesario)

-- ALTER TABLE codigos_cups 
-- ADD CONSTRAINT codigos_cups_codigo_unique UNIQUE (codigo_cups);

-- Crear índice para mejorar el rendimiento de búsquedas
CREATE INDEX IF NOT EXISTS idx_codigos_cups_codigo ON codigos_cups(codigo_cups);

-- Verificar la estructura de la tabla
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'codigos_cups'
ORDER BY ordinal_position;

-- Verificar restricciones
SELECT 
    constraint_name, 
    constraint_type
FROM information_schema.table_constraints 
WHERE table_name = 'codigos_cups';
