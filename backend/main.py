import os
import jwt
import datetime
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Query, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from agents import Runner
from passlib.context import CryptContext
from backend.db import admins_collection
from backend.agent import agent, run_agent, stream_agent
from backend.student_router import router as student_router
from backend.analytics_router import routers as analytics_router

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "12"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    if admins_collection.find_one({"email": email}) is None:
        raise credentials_exception
    
    return email


app = FastAPI(title="Campus Admin Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class AuthRequest(BaseModel):
    email: str
    password: str
    name: str = None  

@app.post("/admin/signup")
def admin_signup(auth_data: AuthRequest):
    email = auth_data.email.lower().strip()
    if admins_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail=f"Admin with email {email} already exists")
    hashed = hash_password(auth_data.password)
    admin = {
        "email": email, 
        "password": hashed, 
        "name": auth_data.name or "", 
        "created_at": datetime.datetime.utcnow(), 
        "verified": True
    }
    admins_collection.insert_one(admin)
    return {"message": "Admin created successfully", "admin": {"email": email, "name": auth_data.name}}

@app.post("/admin/login")
def admin_login(auth_data: AuthRequest):
    email = auth_data.email.lower().strip()
    admin = admins_collection.find_one({"email": email})
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(auth_data.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": admin["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def root():
    return {"message": "AI Campus Admin Agent Server", "status": "running"}

class ChatMessage(BaseModel):
    message: str
    user_id: str

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        response = await run_agent(msg.message)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.post("/chat/stream")
async def chat_stream(msg: ChatMessage):
    async def event_generator():
        try:
            async for token in stream_agent(msg.message):
                yield f"data: {token}\n\n"
        except Exception as e:
            yield f"data: [STREAM ERROR] {str(e)}\n\n"

    return StreamingResponse(
    event_generator(), 
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
)


app.include_router(student_router)
app.include_router(analytics_router)
