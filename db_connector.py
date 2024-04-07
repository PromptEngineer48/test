import os
from sqlalchemy import create_engine, text
import pandas as pd

os.environ.setdefault('BOT_TOKEN','6833712512:AAEF7MuxIhqZAYxQiuPr7lrasid2W8CWv3g')
os.environ.setdefault('DB_USERNAME','postgres_ro')
os.environ.setdefault('DB_PASSWORD','password')
os.environ.setdefault('DB_NAME','VyttahMasters')
os.environ.setdefault('DB_URL','vyttah-database.ceu03herukvs.us-east-1.rds.amazonaws.com')
os.environ.setdefault('OPENAI_API_BASE','http://localhost:11434/v1')
os.environ.setdefault('OPENAI_API_KEY','ollama')


def get_database_connection():
    # Retrieve database credentials from environment variables
    db_user = os.environ.get('DB_USERNAME')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_URL')

    # Use DB_PORT as a string, and no need for explicit conversion
    db_port = 5432

    db_name = os.environ.get('DB_NAME')

    # Create a database connection string
    connection_string = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    # Establish a connection to the database using SQLAlchemy
    engine = create_engine(connection_string)

    return engine


def execute_sql_query(sql_query):
    # Establish a connection to the database using SQLAlchemy
    engine = get_database_connection()

    try:
        # Create a SQLAlchemy text object from the SQL query
        sql_statement = text(sql_query)
        # Use connectable attribute before calling execute
        with engine.connect() as connection:
            result = connection.execute(sql_statement)
            # Fetch the results into a Pandas DataFrame
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
    finally:
        # Close the database connection
        engine.dispose()


