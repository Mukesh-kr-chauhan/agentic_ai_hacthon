from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.config import settings

app = FastAPI(
    title="NetCoop AI — Multi-Agent Network Fault Diagnosis Platform",
    version="1.0.0",
    description="IIT Bhubaneswar Hackathon Finalist System featuring 5 Google Gemini-powered agents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.backend_host, port=settings.backend_port, reload=True)