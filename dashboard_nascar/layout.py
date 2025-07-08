"""
layout.py

Define os componentes visuais do dashboard NASCAR utilizando Dash e Bootstrap Components (dbc).

Este módulo organiza o layout da aplicação em partes reutilizáveis:
- header_layout: cabeçalho com logo, evento, horário e imagem da pista
- status_card: KPIs da corrida (voltas, status, piloto mais rápido)
- tabela_classificacao: DataTable customizado com a classificação ao vivo dos pilotos
- graficos_layout: seção de KPIs visuais (diferença para o líder, abandonos, velocidade média)

Todas as funções retornam elementos `dbc.Row` ou `dbc.Col`, permitindo composição dinâmica no `app.layout`.
"""

import dash_bootstrap_components as dbc
from dash import html, dash_table


def header_layout(nome_pista, inicio, evento, url_imagem):
    """
    Cabeçalho principal do dashboard com logo, informações do evento e imagem do circuito.
    """

    return dbc.Row([
        dbc.Col([
            html.H1([
                html.Img(
                    src="/assets/logo nascar branco.png",
                    style={"height": "90px", "marginRight": "10px"}
                ),
            ]),
            html.Div([
                dbc.Badge(f"🏑 Evento: {evento}", color="danger", className="mb-2 fs-6 fw-semibold"),
                html.Br(),
                dbc.Badge(f"⏱ Início: {inicio}", color="primary", className="fs-6 fw-semibold"),
            ], className="my-2")
        ], md=8),

        dbc.Col([
            dbc.Card([
                dbc.CardImg(src=url_imagem, top=True),
                dbc.CardBody(html.P(f"Circuito: {nome_pista}", className="text-center text-muted mb-0"))
            ], className="shadow rounded")
        ], md=4)
    ], className="my-4")


def status_card():
    """
       Mostra os principais KPIs da corrida em cards horizontais: voltas, piloto mais rápido, status etc.
       """
    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                html.Div(id="voltas-totais", className="display-6 fw-bold text-info"),
                html.Small("Voltas Totais", className="text-muted")
            ])
        ]), className="glass-card rounded-4 shadow-sm", style={"height": "100%"}), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                html.Div(id="volta-atual", className="display-6 fw-bold text-success"),
                html.Small("Volta Atual", className="text-muted")
            ])
        ]), className="glass-card rounded-4 shadow-sm", style={"height": "100%"}), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                html.Div(id="tempo-volta-rapida", className="display-6 fw-bold text-warning"),
                html.Small(id="piloto-volta-rapida", className="text-muted")
            ])
        ]), className="glass-card rounded-4 shadow-sm", style={"height": "100%"}), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                html.Div(id="icone-status", className="display-6"),
                html.Small(id="texto-status", className="text-muted")
            ])
        ]), className="glass-card rounded-4 shadow-sm", style={"height": "100%"}), width=3),
    ], className="g-3 mb-4", align="stretch")


def tabela_classificacao(df_tabela):
    """
        Renderiza a tabela interativa com a classificação ao vivo dos pilotos.
        Aplica estilização customizada com cores por status e efeito "glass".
        """
    return dbc.Row([
        dbc.Col([
            html.H5(" Classificação ao Vivo", className="text-white mb-3"),
            html.Div([
                dash_table.DataTable(
                    id="tabela-classificacao",
                    data=df_tabela.to_dict('records'),
                    columns=[
                        {"name": "Nº", "id": "numero_carro"},
                        {"name": "PILOTO", "id": "nome_completo"},
                        {"name": "CAR", "id": "fabricante"},
                        {"name": "Δ TIME", "id": "delta_tempo"},
                        {"name": "LAP", "id": "volta_atual"},
                        {"name": "PIT", "id": "pit_stops"},
                        {"name": "BEST LAP", "id": "melhor_volta"},
                        {"name": "LAST LAP", "id": "ultima_volta"},
                        {"name": "STATUS", "id": "status"},
                        {"name": "VEL. MÉDIA (mph)", "id": "velocidade_media"}
                    ],
                    page_size=60,
                    style_table={
                        "overflowX": "auto",
                        "backgroundColor": "transparent",
                        "border": "none",
                        "borderRadius": "10px",
                        "padding": "10px",
                        "boxShadow": "0 0 10px rgba(0,0,0,0.3)"
                    },
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "transparent",
                        "color": "white",
                        "padding": "5px",
                        "border": "none",
                        "fontFamily": "Segoe UI",
                        "fontSize": "14px",
                        "whiteSpace": "normal",
                        "height": "auto",
                        "outline": "none",
                        "boxShadow": "none"
                    },
                    style_header={
                        "backgroundColor": "rgba(255,255,255,0.1)",
                        "color": "dark",
                        "fontWeight": "bold",
                        "fontSize": "15px",
                        "border": "none",
                        "textTransform": "uppercase"
                    },
                    style_data={
                        "padding": "12px 8px",
                        "backgroundColor": "transparent",
                        "color": "white",
                        "border": "none"
                    },
                    style_data_conditional=[
                        {"if": {"state": "active"}, "backgroundColor": "rgba(255,255,255,0.04)", "color": "white"},
                        {"if": {"state": "selected"}, "backgroundColor": "rgba(255,255,255,0.04)", "color": "white"},
                        {"if": {"row_index": "odd"}, "backgroundColor": "transparent"},
                        {"if": {"row_index": "even"}, "backgroundColor": "transparent"},
                        {"if": {"filter_query": "{status} = 'Em pista'", "column_id": "status"}, "color": "lime"},
                        {"if": {"filter_query": "{status} = 'Pits'", "column_id": "status"}, "color": "orange"},
                        {"if": {"filter_query": "{status} = 'Fora'", "column_id": "status"}, "color": "red"}
                    ],
                )
            ], className="glass-box")
        ])
    ], className="mb-4")


def graficos_layout():
    """
        KPIs visuais adicionais: diferença para o líder, abandonos e velocidade média.
        """
    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Margem da Vitória", className="text-white"),
            html.H2(id="dif-lider", className="text-light fw-bold"),
            html.Div("⏱️", className="fs-2 text-secondary")
        ], style={"height": "100%", "display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "center"}),
        className="glass-card shadow-sm text-center rounded-4 p-3", style={"minHeight": "170px"}), md=4, sm=6, xs=12),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Abandonos", className="text-white"),
            html.H2(id="abandonos", className="text-light fw-bold"),
            html.Div("❌", className="fs-2 text-secondary")
        ], style={"height": "100%", "display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "center"}),
        className="glass-card shadow-sm text-center rounded-4 p-3", style={"minHeight": "170px"}), md=4, sm=6, xs=12),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Velocidade Média", className="text-white"),
            html.H2(id="velocidade-media", className="text-light fw-bold"),
            html.Div("🏎️", className="fs-2 text-secondary")
        ], style={"height": "100%", "display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "center"}),
        className="glass-card shadow-sm text-center rounded-4 p-3", style={"minHeight": "170px"}), md=4, sm=6, xs=12),
    ], className="mb-5")
