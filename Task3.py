from decimal import Decimal
from datetime import date
from sqlalchemy import create_engine, select
from sqlalchemy import Integer, String, Numeric, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"


    product_name: Mapped[str] = mapped_column(String(20), primary_key=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity_in_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)


engine = create_engine("sqlite:///store.db", echo=False)


with Session(engine) as session:
    print("Items with stock less than 10:\n")
    stmt = (
        select(Item)
        .where(Item.quantity_in_stock < 10)
        .order_by(Item.product_name)
    )

    for i in session.scalars(stmt):
        print(i.product_name, float(i.price), i.quantity_in_stock, i.expiry_date)



with Session(engine) as session:
    print("\nItems that expire in 2025:\n")
    stmt = (
        select(Item)
        .where(
            Item.expiry_date >= date(2025, 1, 1),
            Item.expiry_date <= date(2025, 12, 31),
        )
        .order_by(Item.product_name)
    )

    for i in session.scalars(stmt):
        print(i.product_name, float(i.price), i.quantity_in_stock, i.expiry_date)



with Session(engine) as session:
    product = input("\nEnter the Product Name to Update the Price: ")

  
    item = session.get(Item, product)

    if item is None:
        print("\nNo item found with that name.")
    else:
        item.price += Decimal("0.15")
        session.commit()

        print("\nUpdated item:\n")
        # Refresh from DB (optional, but clear)
        session.refresh(item)
        print(item.product_name, f"{item.price:.2f}", item.quantity_in_stock, item.expiry_date)
