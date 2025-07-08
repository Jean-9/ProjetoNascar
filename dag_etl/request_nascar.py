"""
request_nascar.py

Responsável por acessar a API pública da NASCAR e retornar os dados da corrida em tempo real.

Este módulo realiza uma requisição GET ao endpoint oficial e retorna os dados no formato JSON.
Utilizado por todo o pipeline para obter as informações mais recentes da corrida atual.

Funções:
- get_live_data(): realiza a requisição e retorna os dados em dicionário (ou None em caso de erro)
"""

import requests

API_URL = "https://cf.nascar.com/live/feeds/live-feed.json"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


def get_live_data():
    """
    Faz uma requisição GET à API da NASCAR e retorna os dados em JSON.
    Em caso de erro, retorna None e exibe a mensagem no terminal.
    """
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERRO][request_nascar.py][get_live_data] Falha na requisição: {e}")
        return None


# print(get_live_data())