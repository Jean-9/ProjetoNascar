#  NASCAR Real-Time Dashboard

Projeto completo de Engenharia de Dados com foco em dados **reais e públicos da NASCAR**. O sistema coleta, transforma, armazena e exibe informações atualizadas de cada corrida em tempo real — tudo orquestrado via Airflow e publicado em um dashboard moderno feito com Dash (Plotly + Bootstrap).

---

## Visão Geral

Este projeto simula uma infraestrutura real de dados utilizada em empresas, aplicada ao domínio esportivo. As informações são obtidas diretamente da API pública da NASCAR, processadas com Python e armazenadas em um banco PostgreSQL. Um dashboard interativo exibe a corrida ao vivo com visual moderno e responsivo.

---

## Tecnologias Utilizadas

- **Python 3.12**
- **Docker**
- **Apache Airflow**
- **PostgreSQL**
- **Dash (Plotly + Bootstrap)**
- **SQLAlchemy / Psycopg2**
- **.env para variáveis sensíveis**
- **Nginx (para deploy em produção)**

---

## Funcionalidades

- Coleta automática de dados da NASCAR a cada 30 segundos
- Transformações e validações dos dados via scripts Python
- Armazenamento estruturado em tabelas normalizadas no PostgreSQL
-  Dashboard interativo com:
   - Classificação ao vivo
   - Status da corrida (volta atual, total, piloto da volta rápida etc.)
   - Gráficos de desempenho
   - Informações dos pilotos
- Orquestração diária via Airflow com execução inteligente somente nos dias de corrida
- Ambiente isolado e seguro com VPN entre o servidor e a máquina local

---

## Estrutura de Pastas

projeto_nascar/
├── dag_etl/ # Pipeline ETL com Airflow
│ ├── dag_nascar.py
│ ├── main.py
│ ├── request_nascar.py
│ ├── transform_data.py
│ └── calendario_NASCAR_2025.csv
│
├── dashboard_nascar/ # Dashboard web com Dash
│ ├── app.py
│ ├── layout.py
│ ├── querys.py
│ ├── imagens_circuitos.py
│ ├── utils/
│ │ ├── db_connection.py
│ │ └── .env
│ ├── assets/ # Estilos CSS e imagens
│ │ ├── *.css
│ │ └── *.jpg/png
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md


##  Como Executar Localmente

### Pré-requisitos
- Docker + Docker Compose
- Python 3.12 (para rodar local sem Docker, opcional)
- PostgreSQL (local ou via container)
- API da NASCAR (pública, sem autenticação)

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/projeto_nascar.git
cd projeto_nascar```

```
### 2. Configure o arquivo .env
```
Crie um arquivo .env com as variáveis de conexão com o banco:

DB_HOST=seu_host
DB_NAME=banco
DB_USER=usuario
DB_PASSWORD=senha
DB_PORT=porta
```

### 3. Suba o projeto com Docker
```
docker-compose up --build
```

### 4. Acesse o Dashboard
```
Abra http://localhost:8051 no navegador.
```


### Conceitos Aplicados
Engenharia de Dados Reais com pipeline completo

Boas práticas com .env, modularização e logs

Atualização contínua e agendada com Airflow

Dashboards otimizados para performance e visual

Separação clara entre dados brutos, transformados e apresentados

### Autor
- Jean Albuquerque


### Status do Projeto
- Versão 1.0 Finalizada
- Versão 2.0: Kafka + PySpark + Machine Learning + Streamlit + Grafana (A lançar)

