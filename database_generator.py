from database import users
from sqlalchemy import create_engine

engine = create_engine("sqlite:///members.db", echo=False)

with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS users")

    conn.exec_driver_sql("""
        CREATE TABLE users (
            username      TEXT PRIMARY KEY,
            email         TEXT NOT NULL,
            password      TEXT NOT NULL,
            date_of_birth DATE NOT NULL
        )
    """)

    query = """
        INSERT INTO users (username, email, password, date_of_birth)
        VALUES (?, ?, ?, ?)
    """
    for u in users:
        conn.exec_driver_sql(query,
            (u["username"], u["email"], u["password"], u["date_of_birth"])
        )

print("users table created and populated.")
