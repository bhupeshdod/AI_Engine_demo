import asyncio
from fastapi import HTTPException
from utils.logger import logger
from .folder_operations import FolderOperations
from .file_operations import FileOperations
from .backup_operations import BackupOperations


class S3Service:
    def __init__(self, s3_client, bucket_name):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.folder_ops = FolderOperations(s3_client, bucket_name)
        self.file_ops = FileOperations(s3_client, bucket_name)
        self.backup_ops = BackupOperations(s3_client, bucket_name)

    async def handle_create_chatbot(self, request, messages):
        try:
            base_folder = f"{request.custom_id}/{request.chat_bot}/"
            sub_folders = [
                f"{base_folder}eng/",
                f"{base_folder}eng/UAT/",
                f"{base_folder}eng/UAT/active/",
                f"{base_folder}eng/UAT/backup/",
                f"{base_folder}eng/PRD/",
                f"{base_folder}eng/PRD/active/",
                f"{base_folder}eng/PRD/backup/"
            ]
            results = await self.folder_ops.create_folders(sub_folders)
            return {"message": messages["operation_completed"], "details": results}
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=500, detail=messages["unexpected_error"].format(str(e)))

    async def handle_add_chatbot_lang(self, request, messages):
        try:
            base_folder = f"{request.custom_id}/{request.chat_bot}/"
            if not await self.folder_ops.check_folder_exists(base_folder):
                return {"message": f"{messages['folder_not_exist']}: '{request.custom_id}/{request.chat_bot}'"}

            lang_base_folder = f"{base_folder}{request.lang}/"
            lang_sub_folders = [
                f"{lang_base_folder}UAT/",
                f"{lang_base_folder}UAT/active/",
                f"{lang_base_folder}UAT/backup/",
                f"{lang_base_folder}PRD/",
                f"{lang_base_folder}PRD/active/",
                f"{lang_base_folder}PRD/backup/"
            ]

            results = await self.folder_ops.create_folders(lang_sub_folders)
            return {"message": messages["operation_completed"], "details": results}
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=500, detail=messages["unexpected_error"].format(str(e)))

    async def handle_backup_active(self, custom_id, chat_bot, lang, messages):
        return await self.backup_ops.handle_backup_active(custom_id, chat_bot, lang, messages)

    async def handle_upload_to_chatbot_active(self, custom_id, chat_bot, lang, file, messages):
        try:
            base_folder = f"{custom_id}/{chat_bot}/{lang}/UAT/"
            active_folder = f"{base_folder}active/"
            backup_folder = f"{base_folder}backup/"

            if not await self.folder_ops.check_folder_exists(active_folder):
                raise HTTPException(
                    status_code=404, detail=messages["folder_not_exist"])

            if not await self.folder_ops.check_folder_exists(backup_folder):
                raise HTTPException(
                    status_code=404, detail=messages["folder_not_exist"])

            file_location = f"{active_folder}{file.filename}"
            await self.file_ops.upload_file(file, file_location)

            return {"message": messages["file_uploaded"], "file_location": file_location}
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=500, detail=messages["unexpected_error"].format(str(e)))

    async def handle_restore_active(self, custom_id, chat_bot, lang, backup_file, messages):
        try:
            base_folder = f"{custom_id}/{chat_bot}/{lang}/UAT/"
            active_folder = f"{base_folder}active/"
            backup_folder = f"{base_folder}backup/"

            if not await self.folder_ops.check_folder_exists(active_folder):
                raise HTTPException(
                    status_code=404, detail=messages["folder_not_exist"])

            if not await self.folder_ops.check_folder_exists(backup_folder):
                raise HTTPException(
                    status_code=404, detail=messages["folder_not_exist"])

            backup_file_key = f"{backup_folder}{backup_file}"
            if not await self.folder_ops.check_folder_exists(backup_file_key):
                raise HTTPException(
                    status_code=404, detail=messages["backup_file_not_exist"])

            await self.file_ops.delete_files_in_folder(active_folder)
            await self.file_ops.restore_backup(backup_file_key, active_folder)

            return {"message": messages["rollback_completed"]}
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=500, detail=messages["unexpected_error"].format(str(e)))
