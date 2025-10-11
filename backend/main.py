import datetime
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query, Body, status
from fastapi.middleware.cors import CORSMiddleware

from backend.models import AuthRequest
from backend.db import admins_collection
from backend.auth_utils import hash_password, verify_password, create_access_token, get_current_admin

from backend.student_router import router as student_router
from backend.analytics_router import routers as analytics_router
from backend.chat_router import router as chat_router

app = FastAPI(title="Campus Admin Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "AI Campus Admin Agent Server", "status": "running"}

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
        "created_at": datetime.datetime.now(), 
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

app.include_router(student_router)
app.include_router(analytics_router)
app.include_router(chat_router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
