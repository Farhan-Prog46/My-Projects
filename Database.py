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

def authenticate_user(username: str, password: str) -> bool:
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return True
        return False
    finally:
        session.close()

def store_message(sender:str, content:str):
    session = Session()
    try:
        message = Message(sender= sender, content = content)
        session.add(message)
        session.commit()
    finally:
        session.close()