FROM python:3.12-slim

# Instala dependências de sistema e timezone
RUN apt-get update && apt-get install -y \
    iputils-ping \
    net-tools \
    curl \
    build-essential \
    libpq-dev \
    tzdata \
    && apt-get clean

# Define o timezone do container (São Paulo)
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Cria diretório da aplicação
WORKDIR /app

# Copia arquivos do projeto
COPY . .

# Instala dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expõe a porta do Dash
EXPOSE 8050

# Comando para iniciar o dashboard
CMD ["python", "app.py"]
