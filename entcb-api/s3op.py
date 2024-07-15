from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from auth import AuthService
from models import CreateChatbotRequest, AddLanguageRequest
from utils import load_messages, logger
from utils.s3_service import S3Service
from boto3 import client
from os import getenv

s3op_router = APIRouter()
messages = load_messages()

s3_client = client(
    's3',
    region_name=getenv('DO_SPACES_REGION'),
    endpoint_url=getenv('DO_SPACES_ENDPOINT'),
    aws_access_key_id=getenv('DO_SPACES_ACCESS_KEY'),
    aws_secret_access_key=getenv('DO_SPACES_SECRET_KEY')
)
bucket_name = getenv('BUCKET_NAME')

s3_service = S3Service(s3_client, bucket_name)

@s3op_router.post("/create_chatbot")
async def create_chatbot(request: CreateChatbotRequest, authenticated: bool = Depends(AuthService.authenticate)):
    return await s3_service.handle_create_chatbot(request, messages)

@s3op_router.post("/add_chatbot_lang")
async def add_chatbot_lang(request: AddLanguageRequest, authenticated: bool = Depends(AuthService.authenticate)):
    return await s3_service.handle_add_chatbot_lang(request, messages)

@s3op_router.post("/backup-active")
async def backup_active(custom_id: str, chat_bot: str, lang: str, authenticated: bool = Depends(AuthService.authenticate)):
    return await s3_service.handle_backup_active(custom_id, chat_bot, lang, messages)

@s3op_router.post("/upload-to-chatbot-active")
async def upload_to_chatbot_active(custom_id: str, chat_bot: str, lang: str, file: UploadFile = File(...), authenticated: bool = Depends(AuthService.authenticate)):
    return await s3_service.handle_upload_to_chatbot_active(custom_id, chat_bot, lang, file, messages)

@s3op_router.post("/restore-active")
async def restore_active(custom_id: str, chat_bot: str, lang: str, backup_file: str, authenticated: bool = Depends(AuthService.authenticate)):
    return await s3_service.handle_restore_active(custom_id, chat_bot, lang, backup_file, messages)
