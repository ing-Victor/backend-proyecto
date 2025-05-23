from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Usuario
from pydantic import BaseModel
import hashlib  # Para simular un cifrado básico

from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer

import psutil
import time

app = FastAPI()

load_dotenv()  # Carga variables desde .env si existe

SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_demo")  # Cambia esto por una clave segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Puedes ajustar esto


# Configura los orígenes permitidos (puede ser "*" para permitir todos)
origins = [
    "http://localhost",
    "http://localhost:3000",  # sSi estás sirviendo la web desde un puerto diferente
    "null",
    "file://",                # Opcional, para permitir desde archivos locales
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Aquí puedes usar ["*"] para permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],              # Permitir todos los mét
    allow_headers=["*"],
)

class UsuarioCreate(BaseModel):
    email: str
    password: str

class UsuarioLogin(BaseModel):
    email: str
    password: str

# Dependency para sesión DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read():

    a = 1
    b = 2
    c = a+b
    # Hola Mundo
    return {"message": "holas desde Fast API...", "suma": c}

@app.post("/register")
async def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    password_md5 = hashlib.md5(usuario.password.encode()).hexdigest()
    nuevo_usuario = Usuario(email=usuario.email, password=password_md5)
    #nuevo_usuario = Usuario(email=usuario.email, password=usuario.password)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"message": "Usuario registrado con éxito", "id": nuevo_usuario.id}

# @app.post("/login")
# async def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
#     # Simular "encriptación" usando md5 (NO seguro en producción)
#     password_md5 = hashlib.md5(usuario.password.encode()).hexdigest()

#     user = db.query(Usuario).filter(
#         Usuario.email == usuario.email,
#         Usuario.password == password_md5
#     ).first()

#     if not user:
#         raise HTTPException(status_code=401, detail="Credenciales inválidas")

#     return {"message": "Login exitoso", "email": user.email}

@app.post("/login")
async def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    global attempts  # ← importante para modificar la variable global
    attempts += 1

    # Simular retardo de procesamiento (100ms)
    time.sleep(0.1)

    password_md5 = hashlib.md5(usuario.password.encode()).hexdigest()
    user = db.query(Usuario).filter(
        Usuario.email == usuario.email,
        Usuario.password == password_md5
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail={
            "status": "error",
            "message": "Credenciales inválidas",
            "attempts": attempts
        })

    return {
        "status": "success",
        "message": "Login exitoso",
        "email": user.email,
        "attempts": attempts
    }

def crear_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
@app.post("/token")
async def generar_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    password_md5 = hashlib.md5(form_data.password.encode()).hexdigest()
    user = db.query(Usuario).filter(
        Usuario.email == form_data.username,
        Usuario.password == password_md5
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_token(data={"sub": user.email}, expires_delta=token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/protected_endpoint")
async def leer_usuario_actual(token: str = Depends(oauth2_scheme)):
    payload = verificar_token(token)
    return {"usuario_actual": payload["sub"]}

start_time = time.time()
attempts = 0  # Puedes incrementar este valor manualmente en el endpoint de login para probar


@app.get("/stats")
def get_stats():
    process = psutil.Process()
    memory = process.memory_info()
    cpu_percent = psutil.cpu_percent(interval=0.5)

    return {
        "name": "Victor Gonzalez",
        "attempts": attempts,
        "uptime": int(time.time() - start_time),
        "memoryUsage": {
            "rss": memory.rss,
            "heapTotal": memory.vms,
            "heapUsed": memory.rss
        },
        "cpu": cpu_percent
    }