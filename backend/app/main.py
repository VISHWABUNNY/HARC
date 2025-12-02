from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import tracking, system

app = FastAPI(title="H.A.R.C. System API", version="1.0.0")

# CORS middleware to allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://127.0.0.1:9002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

@app.get("/")
async def root():
    return {"message": "H.A.R.C. System API", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

