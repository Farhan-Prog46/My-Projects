from sqlalchemy import create_engine

engine = create_engine("sqlite:///store.db", echo=False)

with engine.connect() as conn:
    print("Items with stock less than 10:\n")
    result = conn.exec_driver_sql("Select * from items Where quantity_in_stock < 10")

    for row in result:
        print(row)

with engine.connect() as conn:
    print("\nItems that expire in 2025:\n")
    result  = conn.exec_driver_sql("Select * from items Where  expiry_date Like '2025-%'") 
    for row in result:
        print (row)


with engine.connect() as conn:
    product = input("\nEnter the Product Name to Update the Price: ")

    result = conn.exec_driver_sql(f"Update items " 
        f"set price = price + 0.15 "
        f"Where product_name = '{product}'")
     

    print("\nUpdated item:\n")
    result = conn.exec_driver_sql(
        f"SELECT product_name, ROUND(price, 2), quantity_in_stock, expiry_date "
        f"FROM items WHERE product_name = '{product}'")

    for row in result:
        print(row)
    