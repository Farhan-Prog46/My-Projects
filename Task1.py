from data import items
from sqlalchemy import create_engine
 
engine = create_engine("sqlite:///store.db", echo=False)
 
with engine.begin() as conn:
    conn.exec_driver_sql("DROP TABLE IF EXISTS items")
    conn.exec_driver_sql("""
        CREATE TABLE items (
            product_name        VARCHAR(20) NOT NULL,
            price               NUMERIC(10,2) NOT NULL,
            quantity_in_stock   INTEGER NOT NULL,
            expiry_date         DATE NULL
        )
    """)
 
    for i in items:
        conn.exec_driver_sql(
            f"INSERT INTO items (product_name, price, quantity_in_stock, expiry_date) "
            f"VALUES ('{i['product_name']}', "
            f"{float(i['price']):.2f}, "
            f"{int(i['quantity_in_stock'])}, "
            f"'{i['expiry_date']}')"
        )
