"""
querys.py

Responsável por buscar os dados mais recentes da corrida no banco de dados PostgreSQL
para alimentar o dashboard.

A função buscar_info_corrida() retorna um dicionário com DataFrames prontos para visualização:
- Dados da corrida atual
- Dados dos pilotos
- Desempenho por piloto
- Voltas registradas
- Pit stops

A busca se baseia sempre na corrida mais recente (`race_id DESC LIMIT 1`).
"""

import pandas as pd
from utils.db_connection import get_connection


def buscar_info_corrida():
    """
    Consulta os dados mais recentes no banco de dados e retorna um dicionário com:
    - df_corrida
    - df_pilotos
    - df_voltas
    - df_desempenho
    - df_pits

    Returns:
        dict: dicionário com DataFrames pandas prontos para uso no dashboard.
    """
    engine = get_connection()

    # Corrida mais recente
    df_corrida = pd.read_sql("SELECT * FROM corrida ORDER BY race_id DESC LIMIT 1", engine)

    # Todas as entidades relacionadas à última corrida
    race_id = df_corrida["race_id"].iloc[0]
    df_pilotos = pd.read_sql("SELECT * FROM pilotos", engine)
    df_voltas = pd.read_sql("SELECT * FROM voltas_piloto", engine)
    df_desempenho = pd.read_sql(f"SELECT * FROM desempenho_pilotos WHERE race_id = '{race_id}'", engine)
    df_pits = pd.read_sql(f"SELECT * FROM pit_stops WHERE race_id = '{race_id}'", engine)

    return {
        "corrida": df_corrida,
        "pilotos": df_pilotos,
        "voltas_piloto": df_voltas,
        "desempenho": df_desempenho,
        "pits": df_pits
    }
