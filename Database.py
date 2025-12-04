from Models import Base, User, Message
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt

# SQLite file
engine = create_engine("sqlite:///chatroom.db", echo=False)
Session = sessionmaker(bind=engine)

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(engine)

def create_user(email: str, username: str, password: str) -> bool:
    """Create a new user; return True on success, False if duplicate or error."""
    session = Session()
    try:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(email=email, username=username, password_hash=hashed_pw)
        session.add(user)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()

def authenticate_user(username: str, password: str) -> bool:
    """Return True if username/password are correct, else False."""
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False
        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return True
        return False
    finally:
        session.close()

def store_message(sender: str, content: str) -> None:
    """Store one chat message from sender in the database."""
    session = Session()
    try:
        msg = Message(sender=sender, content=content)
        session.add(msg)
        session.commit()
    finally:
        session.close()
