"""
load_data.py

Responsável por inserir os dados transformados no banco de dados PostgreSQL.

Este módulo contém funções de inserção para todas as tabelas do projeto NASCAR:
- corrida
- pilotos
- desempenho_pilotos
- pit_stops
- voltas_piloto
- voltas_processadas (controle de duplicação)

Cada função recebe a conexão `conn` e os dados já tratados (dicionários ou listas de dicionários),
e insere os registros com tratamento para duplicatas usando `ON CONFLICT` ou verificações manuais.

Funções principais:
- insert_corrida(conn, corrida_data)
- insert_pilotos(conn, lista_pilotos)
- insert_desempenho(conn, lista_desempenho)
- insert_pit_stops(conn, lista_paradas)
- insert_voltas(conn, voltas)

Todas as operações são feitas em lote usando `execute_values` para maior desempenho.

Obs:
- `insert_voltas()` inclui controle explícito de duplicidade através da tabela `voltas_processadas`.
- Em caso de falha em alguma operação, recomenda-se usar try/except no script que chama essas funções.
"""

from psycopg2.extras import execute_values


def insert_corrida(conn, corrida_data):
    if not corrida_data:
        print("⚠️ Nenhuma corrida para inserir.")
        return
    """
    Insere os dados gerais da corrida na tabela corrida.
    Se a corrida já existir, ignora (baseado no race_id).
    """
    with conn.cursor() as cur:
        sql = """
            INSERT INTO corrida (
                race_id, nome_pista, inicio, evento,
                voltas_totais, status_corrida, volta_atual,
                piloto_volta_rapida, tempo_volta_rapida, imagem_pista
            )
            VALUES %s
            ON CONFLICT (race_id) DO UPDATE SET
                status_corrida = EXCLUDED.status_corrida,
                volta_atual = EXCLUDED.volta_atual,
                piloto_volta_rapida = EXCLUDED.piloto_volta_rapida,
                tempo_volta_rapida = EXCLUDED.tempo_volta_rapida;
        """
        # Exemplo fictício para 'inicio' e 'imagem_pista', ajuste conforme seu transform
        values = [(
            corrida_data["race_id"],
            corrida_data["nome_pista"],
            corrida_data.get("inicio"),  # você pode usar datetime.now() no main
            corrida_data["evento"],
            corrida_data["voltas_totais"],
            corrida_data["status_corrida"],
            corrida_data["volta_atual"],
            corrida_data["piloto_volta_rapida"],
            corrida_data["tempo_volta_rapida"],
            corrida_data.get("imagem_pista")  # ou None
        )]
        execute_values(cur, sql, values)
    conn.commit()


def insert_pilotos(conn, lista_pilotos):
    if not lista_pilotos:
        print("⚠️ Nenhum piloto para inserir.")
        return
    with conn.cursor() as cur:
        sql = """
            INSERT INTO pilotos (
                driver_id, nome_completo, primeiro_nome,
                ultimo_nome, numero_carro, fabricante
            )
            VALUES %s
            ON CONFLICT (driver_id) DO NOTHING;
        """
        values = [
            (
                p["driver_id"],
                p["nome_completo"],
                p["primeiro_nome"],
                p["ultimo_nome"],
                p["numero_carro"],
                p["fabricante"]
            ) for p in lista_pilotos
        ]
        execute_values(cur, sql, values)
    conn.commit()


def insert_desempenho(conn, lista_desempenho):
    if not lista_desempenho:
        print("⚠️ Nenhuma lista_desempenho para inserir.")
        return
    with conn.cursor() as cur:
        sql = """
            INSERT INTO desempenho_pilotos (
                race_id, driver_id, posicao, delta_tempo,
                volta_atual, pit_stops, melhor_volta,
                ultima_volta, status, velocidade_media, em_pista
            )
            VALUES %s
            ON CONFLICT (race_id, driver_id) DO UPDATE SET
                posicao = EXCLUDED.posicao,
                delta_tempo = EXCLUDED.delta_tempo,
                volta_atual = EXCLUDED.volta_atual,
                pit_stops = EXCLUDED.pit_stops,
                melhor_volta = EXCLUDED.melhor_volta,
                ultima_volta = EXCLUDED.ultima_volta,
                status = EXCLUDED.status,
                velocidade_media = EXCLUDED.velocidade_media,
                em_pista = EXCLUDED.em_pista;
        """
        values = [
            (
                p["race_id"],
                p["driver_id"],
                p["posicao"],
                p["delta_tempo"],
                p["volta_atual"],
                p["pit_stops"],
                p["melhor_volta"],
                p["ultima_volta"],
                p["status"],
                p["velocidade_media"],
                p["em_pista"]
            ) for p in lista_desempenho
        ]
        execute_values(cur, sql, values)
    conn.commit()


def insert_pit_stops(conn, lista_paradas):
    if not lista_paradas:
        print("⚠️ Nenhuma lista_paradas para inserir.")
        return
    with conn.cursor() as cur:
        sql = """
            INSERT INTO pit_stops (
                race_id, driver_id, posicoes_ganhas,
                entrada_tempo, entrada_volta, saida_tempo,
                entrada_rank, saida_rank
            )
            VALUES %s
            ON CONFLICT DO NOTHING;
        """
        values = [
            (
                p["race_id"],
                p["driver_id"],
                p.get("posicoes_ganhas_perdidas"),
                p.get("tempo_entrada"),
                p.get("volta"),
                p.get("tempo_saida"),
                p.get("entrada_rank"),
                p.get("saida_rank")
            ) for p in lista_paradas
        ]
        execute_values(cur, sql, values)
    conn.commit()


def insert_voltas(conn, voltas):
    if not voltas:
        print("⚠️ Nenhuma volta para inserir.")
        return

    with conn.cursor() as cur:
        novas_voltas = []

        for v in voltas:
            driver_id = v["driver_id"]
            numero = v["numero_volta"]
            race_id = v["race_id"]

            # Verifica se já foi processada
            cur.execute("""
                SELECT 1 FROM voltas_processadas
                WHERE race_id = %s AND driver_id = %s AND numero_volta = %s
            """, (race_id, driver_id, numero))

            if cur.fetchone():
                continue  # já inserida

            novas_voltas.append((
                race_id,
                driver_id,
                numero,
                v.get("posicao"),
                v.get("tempo_volta"),
                v.get("velocidade_media")
            ))

        # Insere as novas voltas
        if novas_voltas:
            sql = """
                INSERT INTO voltas_piloto (
                    race_id, driver_id, numero_volta,
                    posicao, tempo_volta, velocidade_media
                )
                VALUES %s
            """
            execute_values(cur, sql, novas_voltas)

            # Agora registra no controle
            cur.executemany("""
                INSERT INTO voltas_processadas (race_id, driver_id, numero_volta)
                VALUES (%s, %s, %s)
            """, [(v[0], v[1], v[2]) for v in novas_voltas])

            print(f"✅ {len(novas_voltas)} novas voltas inseridas.")
        else:
            print("📌 Nenhuma volta nova para inserir.")
