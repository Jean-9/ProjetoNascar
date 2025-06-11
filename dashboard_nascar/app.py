# app.py
import dash
from dash import html, dcc, Output, Input
import plotly.express as px
import pandas as pd
from utils.db_connection import get_connection

app = dash.Dash(__name__)
server = app.server  # Para o deploy com Gunicorn/Nginx

app.layout = html.Div([
    html.H1("🏁 NASCAR Real-Time Dashboard"),
    
    dcc.Graph(id='grafico-desempenho'),

    html.Div(id='ultima-atualizacao', style={'marginTop': 20}),
    
    dcc.Interval(
        id='interval-update',
        interval=30*1000,  # 30 segundos
        n_intervals=0
    )
])

@app.callback(
    Output('grafico-desempenho', 'figure'),
    Output('ultima-atualizacao', 'children'),
    Input('interval-update', 'n_intervals')
)
def atualizar_grafico(n):
    conn = get_connection()
    query = """
        SELECT * FROM desempenho_pilotos
WHERE race_id = 5.568
ORDER BY posicao;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    fig = px.line(df, x="posicao", y="ultima_volta", color="delta_tempo", title="Desempenho por Volta")

    return fig, f"Última atualização: {pd.Timestamp.now().strftime('%H:%M:%S')}"

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
