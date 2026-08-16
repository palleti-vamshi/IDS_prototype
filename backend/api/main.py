from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.scada import router as scada_router


app = FastAPI(
    title="LightX-IDS API",
    description="Backend API for the LightX-IDS Industrial SCADA system",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(scada_router)


@app.get("/")
def root():
    return {
        "message": "LightX-IDS API is running"
    }