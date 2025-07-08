"""Módulo responsável por fornecer a conexão com o banco de dados PostgreSQL."""

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection():
    """
    Cria uma conexão com o banco PostgreSQL usando SQLAlchemy.

    Returns:
        sqlalchemy.engine.base.Engine: Engine pronta para uso com pandas ou execução direta.
    """
    try:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")

        if not all([db_user, db_password, db_host, db_port, db_name]):
            raise ValueError("Uma ou mais variáveis de ambiente estão ausentes no .env")


        engine = create_engine(
            f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        return engine
    except Exception as e:
        raise RuntimeError(f"Erro ao criar engine do PostgreSQL: {e}")