-- script_cria_banco_postgres.sql
-- Criação das tabelas do projeto NASCAR em PostgreSQL

-- =====================
-- Tabela: corrida
-- =====================
CREATE TABLE corrida (
    race_id INTEGER PRIMARY KEY,
    nome_pista TEXT,
    inicio TIMESTAMP,
    evento TEXT,
    voltas_totais INTEGER,
    status_corrida TEXT,
    volta_atual INTEGER,
    piloto_volta_rapida TEXT,
    tempo_volta_rapida NUMERIC,
    imagem_pista TEXT
);

-- =====================
-- Tabela: pilotos
-- =====================

CREATE TABLE pilotos (
    driver_id INTEGER PRIMARY KEY,
    nome_completo TEXT,
    primeiro_nome TEXT,
    ultimo_nome TEXT,
    numero_carro TEXT,
    fabricante TEXT
);

-- =============================
-- Tabela: desempenho_pilotos
-- =============================

CREATE TABLE desempenho_pilotos (
    race_id INTEGER,
    driver_id INTEGER,
    posicao INTEGER,
    delta_tempo NUMERIC,
    volta_atual INTEGER,
    pit_stops INTEGER,
    melhor_volta NUMERIC,
    ultima_volta NUMERIC,
    status TEXT,
    velocidade_media NUMERIC,
    em_pista BOOLEAN,
    PRIMARY KEY (race_id, driver_id),
    FOREIGN KEY (race_id) REFERENCES corrida(race_id),
    FOREIGN KEY (driver_id) REFERENCES pilotos(driver_id)
);

-- =====================
-- Tabela: pit_stops
-- =====================
CREATE TABLE pit_stops (
    race_id INTEGER,
    driver_id INTEGER,
    parada_id SERIAL PRIMARY KEY,
    posicoes_ganhas INTEGER,
    entrada_tempo NUMERIC,
    entrada_volta INTEGER,
    saida_tempo NUMERIC,
    entrada_rank INTEGER,
    saida_rank INTEGER,
    FOREIGN KEY (race_id) REFERENCES corrida(race_id),
    FOREIGN KEY (driver_id) REFERENCES pilotos(driver_id)
);


-- ===========================
-- Tabela: voltas_piloto
-- ===========================
CREATE TABLE voltas_piloto (
    race_id INTEGER,
    driver_id INTEGER,
    numero_volta INTEGER,
    posicao INTEGER,
    tempo_volta NUMERIC,
    velocidade_media NUMERIC,
    PRIMARY KEY (race_id, driver_id, numero_volta),
    FOREIGN KEY (race_id) REFERENCES corrida(race_id),
    FOREIGN KEY (driver_id) REFERENCES pilotos(driver_id)
);

-- ===========================
-- Tabela: voltas_processadas
-- ===========================
-- Controle de duplicação de voltas durante a coleta contínua
CREATE TABLE IF NOT EXISTS voltas_processadas (
    driver_id TEXT,
    numero_volta INTEGER,
    PRIMARY KEY (driver_id, numero_volta)
);