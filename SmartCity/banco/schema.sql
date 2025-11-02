-- Updated schema to use MySQL syntax instead of SQLite
CREATE TABLE IF NOT EXISTS usuarios(
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regioes(
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario (usuario_id),
    UNIQUE KEY unique_user_region (usuario_id, nome)
);

CREATE TABLE IF NOT EXISTS semaforos(
    id INT AUTO_INCREMENT PRIMARY KEY,
    regiao_id INT NOT NULL,
    localizacao VARCHAR(255) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    tempo INT NOT NULL,
    eficiencia FLOAT DEFAULT 0,
    fluxo_veiculos INT DEFAULT 0,
    tempo_verde_real INT DEFAULT 0,
    tempo_amarelo_real INT DEFAULT 0,
    tempo_vermelho_real INT DEFAULT 0,
    taxa_ocupacao FLOAT DEFAULT 0,
    atraso_medio INT DEFAULT 0,
    capacidade_veiculos INT DEFAULT 30,
    pedidos_pedestres INT DEFAULT 0,
    conformidade_padrao FLOAT DEFAULT 0,
    throughput INT DEFAULT 0,
    queue_length INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (regiao_id) REFERENCES regioes(id) ON DELETE CASCADE,
    INDEX idx_regiao (regiao_id)
);

CREATE TABLE IF NOT EXISTS postes(
    id INT AUTO_INCREMENT PRIMARY KEY,
    regiao_id INT NOT NULL,
    localizacao VARCHAR(255) NOT NULL,
    estado INT NOT NULL,
    automatico INT NOT NULL DEFAULT 0,
    eficiencia FLOAT DEFAULT 0,
    potencia_nominal INT DEFAULT 150,
    consumo_real FLOAT DEFAULT 0,
    luminancia_media FLOAT DEFAULT 0,
    iluminancia_minima FLOAT DEFAULT 0,
    iluminancia_media FLOAT DEFAULT 0,
    uniformidade FLOAT DEFAULT 0,
    fator_potencia FLOAT DEFAULT 0,
    tempo_operacao INT DEFAULT 0,
    temperatura_cor INT DEFAULT 4000,
    indice_reproducao_cor INT DEFAULT 70,
    taxa_ocupacao_via INT DEFAULT 0,
    modo_dimming INT DEFAULT 0,
    infrared_detection INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (regiao_id) REFERENCES regioes(id) ON DELETE CASCADE,
    INDEX idx_regiao (regiao_id)
);
