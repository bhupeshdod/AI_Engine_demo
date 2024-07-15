import zipfile
from io import BytesIO
import asyncio
from botocore.exceptions import ClientError
from utils.logger import logger

class FileOperations:
    def __init__(self, s3_client, bucket_name):
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    async def check_folder_exists(self, folder_key):
        try:
            response = await asyncio.to_thread(
                self.s3_client.list_objects_v2, Bucket=self.bucket_name, Prefix=folder_key, MaxKeys=1)
            return 'Contents' in response
        except ClientError as e:
            logger.error(f"ClientError while checking folder: {str(e)}")
            raise

    async def list_files_in_folder(self, folder_key):
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=folder_key)

            files = []
            async for page in page_iterator:
                if 'Contents' in page:
                    files.extend([content['Key'] for content in page['Contents'] if not content['Key'].endswith('/')])
            return files
        except ClientError as e:
            logger.error(f"ClientError while listing files: {str(e)}")
            raise

    async def create_zip_from_files(self, files):
        buffer = BytesIO()
        async with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            tasks = [self._add_file_to_zip(zip_file, file_key) for file_key in files]
            await asyncio.gather(*tasks)
        buffer.seek(0)
        return buffer

    async def _add_file_to_zip(self, zip_file, file_key):
        file_obj = await asyncio.to_thread(self.s3_client.get_object, Bucket=self.bucket_name, Key=file_key)
        file_content = file_obj['Body'].read()
        await asyncio.to_thread(zip_file.writestr, file_key.split('/')[-1], file_content)

    async def upload_file(self, file, file_location):
        await asyncio.to_thread(self.s3_client.upload_fileobj, file.file, self.bucket_name, file_location)

    async def delete_files_in_folder(self, folder_key):
        files = await self.list_files_in_folder(folder_key)
        if files:
            objects_to_delete = [{'Key': file} for file in files]
            await asyncio.to_thread(self.s3_client.delete_objects, Bucket=self.bucket_name, Delete={'Objects': objects_to_delete})

    async def restore_backup(self, backup_file_key, active_folder):
        backup_zip_obj = await asyncio.to_thread(self.s3_client.get_object, Bucket=self.bucket_name, Key=backup_file_key)
        backup_zip_data = BytesIO(backup_zip_obj['Body'].read())
        await self.extract_and_upload_zip(backup_zip_data, active_folder)

    async def extract_and_upload_zip(self, zip_file, destination_folder):
        async with zipfile.ZipFile(zip_file) as zip_file:
            tasks = [self._upload_extracted_file(zip_file, file_name, destination_folder) for file_name in zip_file.namelist()]
            await asyncio.gather(*tasks)

    async def _upload_extracted_file(self, zip_file, file_name, destination_folder):
        file_data = zip_file.read(file_name)
        await asyncio.to_thread(self.s3_client.put_object, Bucket=self.bucket_name, Key=f"{destination_folder}{file_name}", Body=file_data)
