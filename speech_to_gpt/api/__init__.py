from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware


static_path = Path(__file__).parent.parent / "static"
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")
