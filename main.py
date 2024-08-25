from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import router as router
from app.competition_lists_parser import parse_it
from app.database import create_tables, drop_tables
from fastapi.middleware.cors import CORSMiddleware
from app.frontend import router as frontend_router
from app.repositories import ApplicantsRepository
@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_tables()
    await create_tables()

    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(frontend_router)