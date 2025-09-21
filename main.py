from fastapi import FastAPI
from routes import router

app = FastAPI(title="AI Campus Admin Agent")
app.include_router(router)
