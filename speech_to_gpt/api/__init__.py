from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from pathlib import Path


static_path = Path(__file__).parent.parent / "static"
app = FastAPI()


# Serve static files
app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")
