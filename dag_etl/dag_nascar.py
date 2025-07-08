"""
dag_nascar.py

DAG principal do projeto NASCAR.

Executa diariamente às 11h da manhã e aciona o pipeline apenas se houver corrida no dia,
com base no calendário definido em `calendario_NASCAR_2025.csv`.

A função `main()` (importada como `executar_pipeline`) cuida de:
- Verificar se há corrida no dia atual
- Executar a coleta contínua a cada 30 segundos por até 3 horas
- Evitar duplicações e validar os dados antes de inseri-los no banco

Configurações:
- catchup desativado
- 1 execução ativa por vez
- Retry automático em caso de falha leve
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

# Caminho para os scripts do projeto
sys.path.append("/opt/airflow/dags/projeto_nascar")

# Importa a função principal que já cuida de tudo (inclusive verificação de corrida)
from main import main as executar_pipeline

# Dados Padrão
default_args = {
    "owner": "jean",
    "start_date": datetime(2025, 7, 6),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    dag_id="nascar_pipeline_diario",
    default_args=default_args,
    description="Executa o pipeline da NASCAR caso haja corrida no dia",
    schedule_interval="0 11 * * *",  # Executa todos os dias às 11h
    catchup=False,
    max_active_runs=1,
    tags=["nascar", "realtime", "python"],
)

executar = PythonOperator(
    task_id="verificar_corrida_e_executar_pipeline",
    python_callable=executar_pipeline,
    dag=dag,
)

executar