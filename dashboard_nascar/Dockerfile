# Imagem base minimalista com Python 3.12
FROM python:3.12-slim

# Define o fuso horário
ENV TZ=America/Sao_Paulo

# Instala dependências do sistema e configura timezone
RUN apt-get update && apt-get install -y \
    iputils-ping \
    net-tools \
    curl \
    build-essential \
    libpq-dev \
    tzdata \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia apenas o requirements primeiro (melhora cache de build)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe a porta usada pelo Dash
EXPOSE 8050

# Comando padrão para iniciar o app
CMD ["python", "app.py"]