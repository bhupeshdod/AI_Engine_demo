from datetime import datetime
import asyncio
from botocore.exceptions import ClientError
from utils.logger import logger
from .file_operations import FileOperations

class BackupOperations:
    def __init__(self, s3_client, bucket_name):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.file_operations = FileOperations(s3_client, bucket_name)

    def generate_backup_file_name(self, custom_id, chat_bot, lang, seq_num):
        timestamp = datetime.now().strftime('%H%M_%d%b%Y').lower()
        return f"{seq_num:02d}_{timestamp}_{custom_id}_{chat_bot}_{lang}.zip"

    async def upload_backup(self, zip_buffer, backup_folder, backup_file_name):
        backup_file_key = f"{backup_folder}{backup_file_name}"
        await asyncio.to_thread(self.s3_client.upload_fileobj, zip_buffer, self.bucket_name, backup_file_key)

    async def update_backup_log(self, backup_folder, backup_file_name):
        log_file_key = f"{backup_folder}backup_log.txt"
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {backup_file_name}\n"
        log_content = await self._get_log_content(log_file_key)
        log_content += log_entry
        await asyncio.to_thread(self.s3_client.put_object, Bucket=self.bucket_name, Key=log_file_key, Body=log_content)

    async def _get_log_content(self, log_file_key):
        try:
            log_file_obj = await asyncio.to_thread(self.s3_client.get_object, Bucket=self.bucket_name, Key=log_file_key)
            return log_file_obj['Body'].read().decode('utf-8')
        except ClientError:
            return ""

    async def get_next_seq_num(self, seq_file_key):
        try:
            seq_file_obj = await asyncio.to_thread(self.s3_client.get_object, Bucket=self.bucket_name, Key=seq_file_key)
            seq_num = int(seq_file_obj['Body'].read().decode('utf-8').strip())
        except ClientError:
            seq_num = 0

        next_seq_num = seq_num + 1
        if next_seq_num > 29:
            next_seq_num = 1
        await asyncio.to_thread(self.s3_client.put_object, Bucket=self.bucket_name, Key=seq_file_key, Body=str(next_seq_num).zfill(2))
        return next_seq_num

    async def handle_backup_active(self, custom_id, chat_bot, lang, messages):
        try:
            base_folder = f"{custom_id}/{chat_bot}/{lang}/UAT/"
            active_folder = f"{base_folder}active/"
            backup_folder = f"{base_folder}backup/"
            seq_file_key = f"{base_folder}lastseqnum.json"

            if not await self.file_operations.check_folder_exists(active_folder):
                raise HTTPException(status_code=404, detail=messages["folder_not_exist"])

            if not await self.file_operations.check_folder_exists(backup_folder):
                raise HTTPException(status_code=404, detail=messages["folder_not_exist"])

            files_to_backup = await self.file_operations.list_files_in_folder(active_folder)
            if not files_to_backup:
                raise HTTPException(status_code=404, detail=messages["no_files_to_backup"])

            zip_buffer = await self.file_operations.create_zip_from_files(files_to_backup)
            seq_num = await self.get_next_seq_num(seq_file_key)
            backup_file_name = self.generate_backup_file_name(custom_id, chat_bot, lang, seq_num)
            await self.upload_backup(zip_buffer, backup_folder, backup_file_name)
            await self.update_backup_log(backup_folder, backup_file_name)
            await self.file_operations.delete_files_in_folder(active_folder)

            return {"message": messages["backup_completed"], "backup_file": backup_file_name}
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(status_code=500, detail=messages["unexpected_error"].format(str(e)))
