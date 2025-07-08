"""
app.py

Arquivo principal da aplicação Dash do projeto NASCAR.

Este script:
- Inicializa o servidor Dash com tema escuro (Darkly + FontAwesome)
- Conecta-se ao banco via função buscar_info_corrida()
- Monta o layout da aplicação com cards, tabelas e gráficos
- Atualiza dinamicamente as informações da corrida a cada 30 segundos
- Exibe a imagem do circuito, tempo de corrida, status e classificação dos pilotos

Principais componentes:
- status_card: KPIs ao vivo (volta atual, tempo, status)
- tabela_classificacao: tabela interativa dos pilotos
- graficos_layout: seções visuais adicionais ao final do dashboard
- dcc.Interval: força a atualização periódica

Callbacks:
- atualizar_tabela: atualiza os dados da tabela de classificação
- atualizar_status_card: atualiza os cards com KPIs da corrida

Dependências:
- querys.py
- layout.py
- imagens_circuitos.py
"""

import dash
from dash import html, dcc, dash_table, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import numpy

from querys import buscar_info_corrida
from layout import header_layout, status_card, tabela_classificacao, graficos_layout
from imagens_circuitos import circuito_imagens

# ========================
# Inicialização do App
# ========================
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
    ]
)

# ========================
# Funções auxiliares
# ========================

def normalizar_nome_pista(nome):
    """Remove espaços e deixa o nome da pista em minúsculo (para mapear imagens)."""
    return nome.strip().lower()

# ========================
# Mapeamento de status
# ========================
status_map = {
    0: {"texto": "Agendada", "icone": "🕒", "cor": "secondary"},
    1: {"texto": "Bandeira Verde", "icone": "🟢", "cor": "success"},
    2: {"texto": "Bandeira Amarela", "icone": "🟡", "cor": "warning"},
    3: {"texto": "Bandeira Vermelha", "icone": "🔴", "cor": "danger"},
    4: {"texto": "Finalizada", "icone": "🏁", "cor": "primary"},
    5: {"texto": "Encerrada", "icone": "❌", "cor": "danger"},
    6: {"texto": "Suspensa", "icone": "⛔", "cor": "warning"},
    7: {"texto": "Pós-corrida", "icone": "📊", "cor": "info"},
    8: {"texto": "Cancelada", "icone": "🛘", "cor": "dark"},
    9: {"texto": "Desconhecido", "icone": "❓", "cor": "secondary"}
}

# ========================
# Callbacks dinâmicos
# ========================
@app.callback(
    Output("tabela-classificacao", "data"),
    Input("interval-atualizacao", "n_intervals")
)
def atualizar_tabela(n):
    dados = buscar_info_corrida()
    df_desempenho = dados["desempenho"]
    df_pilotos = dados["pilotos"]

    df_tabela = df_desempenho.merge(
        df_pilotos[["driver_id", "numero_carro", "nome_completo", "fabricante"]],
        on="driver_id",
        how="left"
    )
    df_tabela = df_tabela.sort_values(by="volta_atual", ascending=False)

    status_piloto_map = {
        1: "Em pista",
        2: "Pits",
        3: "Fora",
        4: "Acidente",
    }

    df_tabela["status"] = pd.to_numeric(df_tabela["status"], errors="coerce").astype("Int64")
    df_tabela["status"] = df_tabela["status"].map(status_piloto_map).fillna("Desconhecido")

    return df_tabela.to_dict("records")

# Callback para atualizar os cards de status
@app.callback(
    [
        Output("voltas-totais", "children"),
        Output("volta-atual", "children"),
        Output("tempo-volta-rapida", "children"),
        Output("piloto-volta-rapida", "children"),
        Output("icone-status", "children"),
        Output("texto-status", "children")
    ],
    Input("interval-atualizacao", "n_intervals")
)

def atualizar_status_card(n):
    dados = buscar_info_corrida()
    df_corrida = dados["corrida"]

    voltas_totais = df_corrida["voltas_totais"].iloc[0]
    volta_atual = df_corrida["volta_atual"].iloc[0]
    tempo_volta_rapida = df_corrida["tempo_volta_rapida"].iloc[0]
    piloto_volta_rapida = df_corrida["piloto_volta_rapida"].iloc[0]

    status_codigo = df_corrida["status_corrida"].iloc[0]
    status = status_map.get(status_codigo, {"texto": "Desconhecido", "icone": "❓", "cor": "secondary"})

    return (
        f"{voltas_totais}",
        f"{volta_atual}/{voltas_totais}",
        f"{tempo_volta_rapida}s",
        f"Volta Rápida: {piloto_volta_rapida}",
        status["icone"],
        f"Status Corrida: {status['texto']}"
    )

# ========================
# Execução inicial (layout)
# ========================

# Coleta inicial
dados = buscar_info_corrida()
df_corrida = dados["corrida"]
df_pilotos = dados["pilotos"]
df_voltas = dados["voltas_piloto"]
df_desempenho = dados["desempenho"]
df_pits = dados["pits"]

# Pré-processamento da tabela
df_tabela = df_desempenho.merge(
    df_pilotos[["driver_id", "numero_carro", "nome_completo", "fabricante"]],
    on="driver_id",
    how="left"
).sort_values(by="volta_atual", ascending=False)

df_tabela = df_tabela.copy()
df_tabela["status"] = pd.to_numeric(df_tabela["status"], errors="coerce").astype("Int64")
df_tabela["status"] = df_tabela["status"].map({
    1: "Em pista",
    2: "Pits",
    3: "Fora",
    4: "Acidente",
}).fillna("Desconhecido")


# Dados da corrida para o cabeçalho
nome_pista = df_corrida["nome_pista"].iloc[0]
nome_pista_normalizado = normalizar_nome_pista(nome_pista)
url_imagem = circuito_imagens.get(nome_pista_normalizado, "/assets/default.jpg")
inicio = df_corrida["inicio"].iloc[0].strftime("%H:%M UTC")
evento = df_corrida["evento"].iloc[0]
status_code = df_corrida["status_corrida"].iloc[0]
status_info = status_map.get(status_code, {"texto": "Desconhecido", "icone": "❓", "cor": "secondary"})

# KPIs adicionais ao final do dash
velocidade_media_final = round(df_tabela["velocidade_media"].mean(), 1)
dif_lider = df_tabela["delta_tempo"].iloc[1]  # 2º colocado
abandonos = df_tabela[df_tabela["status"] == "Fora"].shape[0]

# ========================
# Layout principal
# ========================

app.layout = dbc.Container(fluid=True, children=[
    header_layout(nome_pista, inicio, evento, url_imagem),
    status_card(),
    tabela_classificacao(df_tabela),
    graficos_layout(),

    dcc.Interval(
        id="interval-atualizacao",
        interval=30 * 1000,
        n_intervals=0
    )
])

# ========================
# Execução do app
# ========================
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
