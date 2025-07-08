"""
transform_data.py

Responsável por transformar os dados brutos da API da NASCAR em estruturas organizadas
para posterior inserção no banco de dados.

Este módulo realiza:
- Filtros por categoria (apenas Cup Series)
- Extração e formatação de dados da corrida, pilotos, desempenho, pit stops e voltas
- Controle para evitar duplicidade de voltas

Funções principais:
- filter_cup_series(data): filtra apenas corridas da Cup Series
- transformar_corrida(json): transforma os dados gerais da corrida
- pilotos(veiculos): extrai dados dos pilotos
- desempenho_pilotos(veiculos, dados_corrida): extrai desempenho por piloto
- extrair_pit_stops(veiculos, race_id): organiza dados de pit stop
- voltas_veiculo(veiculos, race_id, ultima_volta_salva): extrai última volta por piloto com controle de duplicação
"""

SERIES_CUP_ID = 1  # Cup Series


def filter_cup_series(data):
    """Retorna os dados apenas se for uma corrida da Cup Series."""
    if not data:
        return None

    if data.get("series_id") == SERIES_CUP_ID:
        return data
    else:
        return None


def piloto_volta_rapida_corrida(veiculos):
    """
       Retorna o piloto com a volta mais rápida da corrida (entre todos os veículos).
       """
    piloto_mais_rapido = None
    tempo_mais_rapido = float("inf")

    for veiculo in veiculos:
        piloto = veiculo.get("driver", {}).get("full_name")
        tempo = veiculo.get("best_time")

        if tempo and tempo < tempo_mais_rapido:
            tempo_mais_rapido = tempo
            piloto_mais_rapido = piloto

    if piloto_mais_rapido is None:
        return {
            "piloto": None,
            "tempo": None
        }

    return {
        "piloto": piloto_mais_rapido,
        "tempo": tempo_mais_rapido
    }


def volta_mais_rapida_da_volta_atual(veiculos):
    """
     Retorna o piloto com a volta mais rápida na volta atual.
     """
    piloto_mais_rapido = None
    tempo_mais_rapido = float("inf")

    for v in veiculos:
        tempo = v.get("best_lap_time")
        piloto = v.get("driver", {}).get("full_name")

        if tempo and tempo < tempo_mais_rapido:
            tempo_mais_rapido = tempo
            piloto_mais_rapido = piloto

    if piloto_mais_rapido is None:
        return {
            "piloto": None,
            "tempo": None
        }

    return {
        "piloto": piloto_mais_rapido,
        "tempo": tempo_mais_rapido
    }


def transformar_corrida(json):
    """
        Transforma os dados brutos da corrida em uma estrutura organizada para inserção no banco.
        """
    dados_corrida = json
    veiculos = json["vehicles"]
    volta_atual = dados_corrida["lap_number"]

    info_volta_rapida = volta_mais_rapida_da_volta_atual(veiculos)

    return {
        "race_id": dados_corrida["race_id"],
        "nome_pista": dados_corrida["track_name"],
        # "inicio"
        "evento": dados_corrida["run_name"],
        "voltas_totais": dados_corrida["laps_in_race"],
        "status_corrida": dados_corrida["flag_state"],
        "volta_atual": volta_atual,
        "piloto_volta_rapida": info_volta_rapida["piloto"],
        "tempo_volta_rapida": info_volta_rapida["tempo"]
        # "imagem_pista" adicionados na hora do insert
    }


def pilotos(veiculos):
    """
       Retorna uma lista de pilotos com informações básicas para inserção.
       """
    lista_pilotos = []

    for veiculo in veiculos:
        piloto = {
            "driver_id": veiculo["driver"]["driver_id"],
            "nome_completo": veiculo["driver"]["full_name"],
            "primeiro_nome": veiculo["driver"]["first_name"],
            "ultimo_nome": veiculo["driver"]["last_name"],
            "numero_carro": veiculo["vehicle_number"],
            "fabricante": veiculo["vehicle_manufacturer"]
        }
        lista_pilotos.append(piloto)
    return lista_pilotos


def tratar_delta(delta):
    """
      Trata o valor de delta (tempo de distância do líder). Converte para float ou 0.0.
      """
    if delta in ["LEADER", "", "--", None]:
        return 0.0
    try:
        return float(delta)
    except ValueError:
        return None


def desempenho_pilotos(veiculos, dados_corrida):
    """
       Extrai o desempenho individual de cada piloto.
       """
    lista_pilotos = []
    race_id = dados_corrida["race_id"]
    volta_atual = dados_corrida["lap_number"]

    for v in veiculos:
        piloto = {
            "race_id": race_id,
            "driver_id": v.get("driver", {}).get("driver_id"),
            "posicao": v.get("running_position"),
            "delta_tempo": tratar_delta(v.get("delta")),
            "volta_atual": volta_atual,
            "pit_stops": len(v.get("pit_stops", [])),
            "melhor_volta": v.get("best_lap"),
            "ultima_volta": v.get("last_lap_time"),
            "status": v.get("status"),
            "velocidade_media": v.get("average_speed"),
            "em_pista": v.get("is_on_track"),
        }
        lista_pilotos.append(piloto)
    return lista_pilotos


def extrair_pit_stops(veiculos, race_id):
    """
       Extrai e organiza os dados de pit stops de cada piloto.
       """
    lista_pit_stops = []

    for v in veiculos:
        driver_id = v["driver"]["driver_id"]
        paradas = v.get("pit_stops", [])

        for p in paradas:
            parada = {
                "race_id": race_id,
                "driver_id": driver_id,
                "posicoes_ganhas": p.get("positions_gained_lossed"),
                "entrada_tempo": p.get("pit_in_elapsed_time"),
                "entrada_volta": p.get("pit_in_lap_count"),
                "saida_tempo": p.get("pit_out_elapsed_time"),
                "entrada_rank": p.get("pit_in_rank"),
                "saida_rank": p.get("pit_out_rank")
            }
            lista_pit_stops.append(parada)

    return lista_pit_stops


def voltas_veiculo(veiculos, race_id, ultima_volta_salva):
    """
        Extrai os dados da última volta completada por cada piloto,
        com controle para evitar duplicação durante a execução contínua.
        """
    lista_voltas = []

    for v in veiculos:
        driver_id = v["driver"]["driver_id"]
        numero_volta = v.get("laps_completed")
        tempo_volta = v.get("last_lap_time")
        velocidade_media = v.get("last_lap_speed")
        posicao = v.get("running_position")

        chave = (race_id, driver_id)

        # Evita registrar a mesma volta mais de uma vez
        if numero_volta and tempo_volta:
            if ultima_volta_salva.get(chave) != numero_volta:
                ultima_volta_salva[chave] = numero_volta  # atualiza controle

                registro = {
                    "race_id": race_id,
                    "driver_id": driver_id,
                    "numero_volta": numero_volta,
                    "posicao": posicao,
                    "tempo_volta": tempo_volta,
                    "velocidade_media": velocidade_media
                }
                lista_voltas.append(registro)

    return lista_voltas
