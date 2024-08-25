import asyncio
from fastapi import APIRouter, HTTPException, WebSocket
from fastapi import Request
from app.competition_lists_parser import parse_it
from fastapi.responses import FileResponse
import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os
from app.repositories import ApplicantsRepository
router = APIRouter()
lock = asyncio.Lock()

# @router.get("/applicants-api/applicants/{snils}")
# async def return_user(request: Request, snils: str):
#     global lock
#     if await UsersRepository.get_timёe_update():
#         if lock.locked():
#             return {"data": "Parsing is in progress "}
#         async with lock:
#             print("Parsing is started")
#             await parse_it()
#             await UsersRepository.update_users()
#             await get_database()
#             print("Parsing is done")
#     else:
#         user_info = await UsersRepository.get_user_by_snils(snils)
#         return {"user_info": user_info}
#     user_info = await UsersRepository.get_user_by_snils(snils)
#     return {"user_info": user_info}

# @router.get("/applicants-api/download-output")
# async def download_output_file():
#     file_path = "/output.xlsx"
#     return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename='output.xlsx')

# Маршрут для обработки загруженного файла
status_channels = {}

@router.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_id = id(websocket)
    status_channels[connection_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        del status_channels[connection_id]

@router.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file format. Only .xlsx files are allowed.")

    file_location = f"uploaded_files/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    await update_status("Обработка файла, пожалуйста подождите...")
    await ApplicantsRepository.process_xlsx(file_location)
    await update_status("Синхронизация с таблицей ПГНИУ...")
    await parse_it()
    await update_status("Завершено!")

async def update_status(message: str):
    await asyncio.gather(*(channel.send_text(message) for channel in status_channels.values()))



@router.post("/update_seats/{group_uuid}")
async def update_seats(group_uuid: str, seats: int = Form(...)):
    await ApplicantsRepository.update_seats(group_uuid, seats)
    return {"info": f"Seats for group {group_uuid} updated to {seats}"}
