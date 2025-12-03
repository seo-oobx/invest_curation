from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import events, alerts

app = FastAPI(title="Alpha Calendar API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
from app.api.endpoints import admin
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

from app.services.scheduler import scheduler_service

@app.on_event("startup")
async def startup_event():
    scheduler_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler_service.shutdown()

@app.get("/")
def read_root():
    return {"message": "Welcome to Alpha Calendar API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
