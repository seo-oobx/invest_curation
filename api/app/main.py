from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import events, alerts

app = FastAPI(title="Alpha Calendar API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Alpha Calendar API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
