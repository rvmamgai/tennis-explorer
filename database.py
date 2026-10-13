import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_config(key):
    """Reads a setting from Streamlit secrets (when deployed on Streamlit Cloud)
    or from the local .env file (when running on your own machine), whichever is available."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)


DB_USER = get_config("DB_USER")
DB_PASSWORD = get_config("DB_PASSWORD")
DB_HOST = get_config("DB_HOST")
DB_PORT = int(get_config("DB_PORT"))
DB_NAME = get_config("DB_NAME")

connection_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_url, connect_args={"ssl": {"ssl_mode": "REQUIRED"}})


def load_table(table_name, rows, update_columns):
    """Insert rows into a table. If a row's primary key already exists, update it instead."""
    if not rows:
        print(f"No rows to load into {table_name}")
        return

    columns = list(rows[0].keys())
    column_list = ", ".join(f"`{col}`" for col in columns)
    placeholders = ", ".join(f":{col}" for col in columns)
    update_clause = ", ".join(f"`{col}` = VALUES(`{col}`)" for col in update_columns)

    sql = text(f"""
        INSERT INTO {table_name} ({column_list})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(sql, rows)

    print(f"Loaded {len(rows)} rows into {table_name}")


if __name__ == "__main__":
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Connected! Test query result:", result.fetchone())