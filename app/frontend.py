from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os
from fastapi import APIRouter
from app.repositories import ApplicantsRepository

router = APIRouter(
    tags=["Main Page"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def main(request: Request):
    # groups = await ApplicantsRepository.get_contest_groups()
    return templates.TemplateResponse("main.html", {"request": request})
