from fastapi import FastAPI
from fastapi_pagination import add_pagination  # type: ignore
from app.routers import api_router

app = FastAPI(title="WorkoutApi")
app.include_router(api_router)

add_pagination(app)
