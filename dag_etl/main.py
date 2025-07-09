"""
main.py

Arquivo principal do pipeline NASCAR.

Este script é responsável por:
- Verificar se há corrida da Cup Series no dia atual (com base no CSV de calendário)
- Coletar dados em tempo real da API da NASCAR a cada 30 segundos (durante 3 horas)
- Transformar os dados brutos em estruturas organizadas
- Inserir os dados nas tabelas correspondentes no PostgreSQL
- Garantir que não haja duplicidade de voltas por piloto
- Permitir execução contínua via Airflow ou execução direta manual

Principais funções:
- main(): ponto de entrada da DAG (usado no Airflow)
- executar_pipeline(): realiza uma execução completa do ciclo ETL
- coleta_continua(): executa o ciclo completo repetidamente por 3h
- buscar_e_salvar_dados(): wrapper usado em algumas DAGs

Dependências:
- transform_data.py
- load_data.py
- Calendario_NASCAR_2025.csv
"""

import time
import pandas as pd
import psycopg2
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# from mensagem_telegram import enviar_telegram
from transform_data import (
    filter_cup_series,
    transformar_corrida,
    pilotos,
    desempenho_pilotos,
    extrair_pit_stops,
    voltas_veiculo
)
from load_data import (
    insert_corrida,
    insert_pilotos,
    insert_desempenho,
    insert_pit_stops,
    insert_voltas
)

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do arquivo .env

# ===============================
# CONFIGURAÇÕES E CONTROLES
# ===============================

URL = "https://cf.nascar.com/live/feeds/live-feed.json"
ultima_volta_salva = {}  # controle local para evitar duplicação na mesma execução

# ===============================
# FUNÇÕES AUXILIARES
# ===============================

def conectar_banco():
    """Estabelece conexão com o banco PostgreSQL usando variáveis do .env."""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    except Exception as e:
        print(f"[ERRO][main.py][conectar_banco] Falha na conexão com o banco: {e}")
        raise

def coletar_dados():
    try:
        resposta = requests.get(URL, timeout=10)
        resposta.raise_for_status()
        return resposta.json()
    except Exception as e:
        print(f"[ERRO][main.py][coletar_dados] Erro ao acessar API da NASCAR: {e}")
        return None


def corrida_ativa_hoje():
    try:
        calendario = pd.read_csv("Calendario_NASCAR_2025.csv")

        # Converte para datetime com timezone de origem (EUA)
        calendario["data"] = pd.to_datetime(calendario["data"]).dt.tz_localize(ZoneInfo("America/New_York"))

        # Converte para fuso horário do Brasil
        calendario["data"] = calendario["data"].dt.tz_convert(ZoneInfo("America/Sao_Paulo"))

        # Extrai apenas a data (sem hora) para comparar com hoje em BR
        calendario["data"] = calendario["data"].dt.date

        hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()

        if hoje in calendario["data"].values:
            print("[INFO][main.py] Corrida agendada para hoje.")
            return True
        else:
            print("[INFO][main.py] Nenhuma corrida programada para hoje.")
            return False

    except Exception as e:
        print(f"[ERRO][main.py][corrida_ativa_hoje] Falha ao ler o calendário: {e}")
        return False

# ===============================
# FUNÇÃO DE EXECUÇÃO DO PIPELINE
# ===============================

def executar_pipeline():
    json_data = coletar_dados()
    if not json_data:
        print("[INFO][main.py][executar_pipeline] JSON da API vazio ou com erro. Encerrando execução.")
        return

    if not filter_cup_series(json_data):
        print("[INFO][main.py][executar_pipeline] Corrida da Cup Series não encontrada.")
        return

    conn = conectar_banco()

    try:
        dados_corrida = transformar_corrida(json_data)
        dados_corrida["inicio"] = datetime.now()
        dados_corrida["imagem_pista"] = None

        lista_pilotos = pilotos(json_data["vehicles"])
        lista_desempenho = desempenho_pilotos(json_data["vehicles"], json_data)
        lista_pit_stops = extrair_pit_stops(json_data["vehicles"], json_data["race_id"])
        lista_voltas = voltas_veiculo(json_data["vehicles"], json_data["race_id"], ultima_volta_salva)

        print("👉 Inserindo corrida...")
        insert_corrida(conn, dados_corrida)

        print("👉 Inserindo pilotos...")
        insert_pilotos(conn, lista_pilotos)

        print("👉 Inserindo desempenho...")
        insert_desempenho(conn, lista_desempenho)

        print("👉 Inserindo pit stops...")
        insert_pit_stops(conn, lista_pit_stops)

        print("👉 Inserindo voltas...")
        insert_voltas(conn, lista_voltas)

        print(f"[OK] Dados atualizados com sucesso para a corrida {dados_corrida['race_id']}")
        # enviar_telegram(f"✅ NASCAR atualizada! Corrida {dados_corrida['race_id']}")

    except Exception as e:
        print(f"[ERRO][main.py][executar_pipeline] Falha geral no processamento: {e}")
        # enviar_telegram(f"❌ Erro na atualização da NASCAR: {e}")
    finally:
        conn.close()

def coleta_continua():
    duracao = 3 * 60 * 60  # 3 horas
    intervalo = 30  # 30 segundos
    ciclos = duracao // intervalo

    print(f"[INFO] Iniciando coleta contínua: {ciclos} ciclos de {intervalo}s")
    for i in range(ciclos):
        print(f"[INFO] Coleta #{i + 1}/{ciclos}")
        executar_pipeline()
        time.sleep(intervalo)

def buscar_e_salvar_dados():
    try:
        executar_pipeline()
    except Exception as e:
        print(f"[ERRO][main.py][buscar_e_salvar_dados] Falha durante execução do pipeline: {e}")

# ===============================
# MAIN
# ===============================

def main():
    print("[INFO][main.py] Verificando calendário de corridas...")
    if not corrida_ativa_hoje():
        print("[INFO][main.py] Hoje não tem corrida. Encerrando pipeline.")
        return

    print("[INFO][main.py] Corrida detectada. Iniciando coleta contínua...")
    coleta_continua()

# Executa se chamado diretamente
if __name__ == "__main__":
    main()