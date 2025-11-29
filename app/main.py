import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from fastapi import FastAPI, Response, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime ,timedelta
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from translate import translate_en_to_fr, translate_fr_to_en
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

# Database credentials
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_NAME = os.getenv("dbname")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app = FastAPI()
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("✓ Connection successful!")
except Exception as e:
    print(f"✗ Failed to connect: {e}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime)

Base.metadata.create_all(bind=engine)

class UserInDB(BaseModel):
    firstname: str
    lastname: str
    username: str
    password: str
    created_at: datetime=None 
    
class LoginModel(BaseModel):
    username: str
    password: str

    
class Translations(Base):
    __tablename__ = "translations"
    id = Column(Integer, primary_key=True, index=True)
    text=Column(String)
    translated_text=Column(String)
Base.metadata.create_all(bind=engine)


class TranslationsInDB(BaseModel):
    text:str
    # translated_text:str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
@app.post('/register')
def register(user: UserInDB, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=403, detail="User already exist")

    new_user = User(
        firstname=user.firstname,
        lastname=user.lastname,
        username=user.username,
        password=pwd_context.hash(user.password),
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post('/login')
def login(user: LoginModel, response: Response, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not pwd_context.verify(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": existing_user.username, "id": existing_user.id},
        expires_delta=access_token_expires
    )
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )
    
    return {
        "message": "Login successful",
        "user": {
            "id": existing_user.id,
            "username": existing_user.username,
            "firstname": existing_user.firstname,
            "lastname": existing_user.lastname
        }
    }


@app.post('/en_to_fr')
def translate_to_fr(data:TranslationsInDB,db:Session=Depends(get_db)):
    translated_text=translate_en_to_fr(data.text)
    new_translation=Translations(
        text=data.text,
        translated_text=translated_text
    )
    db.add(new_translation)
    db.commit()
    db.refresh(new_translation)

    return{
        "original":data.text,
    "translated_text": translated_text
    }

@app.post('/fr_to_en')
def translate_to_en(data:TranslationsInDB,db:Session=Depends(get_db)):
    translated_text = translate_fr_to_en(data.text)
    new_translation=Translations(
        text=data.text,
        translated_text=translated_text
    )
    db.add(new_translation)
    db.commit()
    db.refresh(new_translation)
    return{
    "original": data.text,
    "translated_text": translated_text
    }
    