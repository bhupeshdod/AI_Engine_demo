from fastapi import APIRouter, HTTPException
from app.models import CreateChatbotRequest, AddLanguageRequest
from app.auth import validate_client_keys
from app.s3_utils import create_folders, check_folder_exists, BUCKET_NAME

router = APIRouter()

@router.post("/create_chatbot")
async def create_chatbot(request: CreateChatbotRequest):
    if not await validate_client_keys(request.access_key, request.secret_key):
        raise HTTPException(status_code=403, detail="Invalid access key or secret key")

    base_folder = f"{request.client_id}/{request.chat_bot}/"
    sub_folders = [
        f"{base_folder}eng/",
        f"{base_folder}eng/UAT/",
        f"{base_folder}eng/UAT/active/",
        f"{base_folder}eng/UAT/backup/",
        f"{base_folder}eng/PRD/",
        f"{base_folder}eng/PRD/active/",
        f"{base_folder}eng/PRD/backup/"
    ]

    results = await create_folders(BUCKET_NAME, sub_folders)
    return {"message": "Operation completed", "details": results}

@router.post("/add_chatbot_lang")
async def add_chatbot_lang(request: AddLanguageRequest):
    if not await validate_client_keys(request.access_key, request.secret_key):
        raise HTTPException(status_code=403, detail="Invalid access key or secret key")

    base_folder = f"{request.client_id}/{request.chat_bot}/"
    if not await check_folder_exists(BUCKET_NAME, base_folder):
        raise HTTPException(status_code=404, detail=f"Folder '{request.client_id}/{request.chat_bot}' does not exist")

    lang_base_folder = f"{base_folder}{request.lang}/"
    lang_sub_folders = [
        f"{lang_base_folder}UAT/",
        f"{lang_base_folder}UAT/active/",
        f"{lang_base_folder}UAT/backup/",
        f"{lang_base_folder}PRD/",
        f"{lang_base_folder}PRD/active/",
        f"{lang_base_folder}PRD/backup/"
    ]

    results = await create_folders(BUCKET_NAME, lang_sub_folders)
    return {"message": "Operation completed", "details": results}
