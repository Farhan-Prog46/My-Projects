from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine, select, \
    delete, Integer, String, Numeric, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "Users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable = False)


engine = create_engine("sqlite:///users.db", echo=False)

with Session(engine) as session:
    print("\nAll Users:")

for u in session.scalars(select(User).order_by(User.user_id)):
    print(u.user_id, u.first_name, u.last_name, float(u.balance))

with Session(engine) as session:
    row = session.execute(select(User).where(User.first_name =="Alice")).scalars().one_or_none()

    if row in None:
        print("\nUser 'Alice' not found.")
    else:
        print("\nDetails of user 'Alice':")
        print(f"{row.user_id}, {row.first_name}, {row.last_name}, {float(row.balance)}")

    with Session(engine) as sesssion:
        print("\nUser with balance less than 10.00:")
        for u in session.scalars(select(User).where(User.balance < Decimal("10.00")).order_by(User.user_id)):
            print(u.user_id, u.first_name, u.last_name, float(u.balance))

    with Session(engine) as session:
        u1  = session.get(User, 1)
        if u1:
            u1.balance += Decimal("10.00")
            session.commit()
        u2 = session.get(User, 2)
        if u2:
            u2.last_name = "Thompson"
            session.commit()

