from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.responses import JSONResponse

Base = declarative_base()

# User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(1024), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Memory model
class Memory(Base):
    __tablename__ = 'memory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    memory = Column(Text, nullable=False)

# Conversation model
class Conversation(Base):
    __tablename__ = 'conversation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

## depth 0 Helper Functions

# Create a new user
def create_user(user_id: str, name: str, password: str, email : str, db: Session):
    # Check if the email already exists in the database
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return JSONResponse(status_code=400, content={"message": "Duplicate email_id"})
    
    # If email doesn't exist, create a new user
    db_user = User(user_id=user_id, name=name, email=email)
    db_user.set_password(password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return JSONResponse(status_code=201, content={"user_id": user_id})

def user_login(email: str, password: str, db: Session):
    # Check if the email exists in the database
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return JSONResponse(status_code=400, content={"message": "email_id not found"})
    
    # Check if the password is correct
    if not user.check_password(password):  # Assuming the User model has a check_password method
        return JSONResponse(status_code=400, content={"message": "Incorrect passowrd"})
    
    # If both email and password match, return the user_id
    return {"user_id": user.user_id}    


# Read user by user_id
def get_user_by_id(user_id: str, db: Session):
    return db.query(User).filter(User.user_id == user_id).first()

# Update user details
def update_user(user_id: str, name: str = None, password: str = None, db: Session = None):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user:
        if name:
            db_user.name = name
        if password:
            db_user.set_password(password)
        db.commit()
        db.refresh(db_user)
    return True

# Delete user
def delete_user(user_id: str, db: Session):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return True

# Dependency to get the DB session
DATABASE_URL = "postgresql://nishant:nova123456@localhost:5432/nova_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to update memory
def update_memory(user_id: str, memory: str, db: Session):
    return store_memory(db=db, user_id=user_id, memory=memory)

# Route to get memory
def read_memory(user_id: str, db: Session):
    memory = get_memory(db=db, user_id=user_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

# Route to add a conversation message
def add_conversation(user_id: str, role: str, message: str, db: Session):
    return store_conversation(db=db, user_id=user_id, role=role, message=message)

# Route to get conversation
def read_conversation(user_id: str, db: Session):
    conversation_records = get_conversation(db=db, user_id=user_id)
    
    # Check if there are any conversation records
    if not conversation_records:
        return "Conversation not found."

    # Concatenate the conversation into a single string
    conversation_str = ""
    for record in conversation_records:
        conversation_str += f"{record.role}: {record.message}\n"
    
    return conversation_str.strip()  # Remove the trailing newline


## depth 1 Helper Functions

# Store or update memory for a user
def store_memory(db: Session, user_id: str, memory: str):
    db_memory = db.query(Memory).filter(Memory.user_id == user_id).first()
    if db_memory:
        db_memory.memory = memory
    else:
        db_memory = Memory(user_id=user_id, memory=memory)
        db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory

# Retrieve memory for a user
def get_memory(db: Session, user_id: str):
    memory_record = db.query(Memory).filter(Memory.user_id == user_id).first()
    return memory_record.memory if memory_record else ""

# Store a conversation message
def store_conversation(db: Session, user_id: str, role: str, message: str):
    db_conversation = Conversation(user_id=user_id, role=role, message=message)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

# Retrieve conversation for a user
def get_conversation(db: Session, user_id: str):
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.timestamp).all()


