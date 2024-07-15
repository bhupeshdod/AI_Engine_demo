import asyncio
from botocore.exceptions import ClientError
from utils.logger import logger

class FolderOperations:
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

    async def create_folders(self, folders):
        results = []
        tasks = [self._create_folder(folder) for folder in folders]
        folder_results = await asyncio.gather(*tasks)
        results.extend(folder_results)
        return results

    async def _create_folder(self, folder):
        if not await self.check_folder_exists(folder):
            await asyncio.to_thread(self.s3_client.put_object, Bucket=self.bucket_name, Key=folder)
            return {"folder": folder, "status": "created"}
        return {"folder": folder, "status": "already exists"}
