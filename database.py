from Models import Base, User, Message
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt


engine = create_engine("sqlite:///chat.db", echo=False)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def create_user(username: str, password: str) -> bool:
    session = Session()
    try:
        
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user = User(username=username, password_hash=hashed_pw)
        session.add(user)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()

