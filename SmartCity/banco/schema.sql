-- Updated schema to use MySQL syntax instead of SQLite
CREATE TABLE IF NOT EXISTS usuarios(
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS semaforos(
    id INT AUTO_INCREMENT PRIMARY KEY,
    localizacao VARCHAR(255) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    tempo INT NOT NULL
);

CREATE TABLE IF NOT EXISTS postes(
    id INT AUTO_INCREMENT PRIMARY KEY,
    localizacao VARCHAR(255) NOT NULL,
    estado INT NOT NULL,
    atomatico INT NOT NULL DEFAULT 0
);
