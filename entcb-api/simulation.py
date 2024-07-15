import asyncio
import json
from unittest.mock import AsyncMock
from botocore.exceptions import ClientError
from utils.s3_service.backup_operations import BackupOperations
from datetime import datetime, timedelta

# Mock S3 client
class MockS3Client:
    def __init__(self):
        self.storage = {}

    async def put_object(self, Bucket, Key, Body):
        self.storage[Key] = Body

    async def get_object(self, Bucket, Key):
        if Key in self.storage:
            return {'Body': MockS3Body(self.storage[Key])}
        else:
            raise ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")

    def list_objects_v2(self, Bucket, Prefix, MaxKeys):
        return {'Contents': [key for key in self.storage if key.startswith(Prefix)]}

class MockS3Body:
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data

# Messages mock
messages = {
    "folder_not_exist": "The specified folder does not exist",
    "no_files_to_backup": "No files found in the active folder to backup",
    "backup_completed": "Backup completed successfully",
    "unexpected_error": "An unexpected error occurred: {}",
}

async def simulate_backup():
    mock_s3_client = MockS3Client()
    bucket_name = "test-bucket"
    
    # Pre-populate with mock data
    mock_s3_client.storage["custom_id/chat_bot/lang/UAT/active/file1.txt"] = b"File 1 content"
    mock_s3_client.storage["custom_id/chat_bot/lang/UAT/active/file2.txt"] = b"File 2 content"
    
    # Initialize BackupOperations
    backup_ops = BackupOperations(mock_s3_client, bucket_name)
    
    # Simulate 35 backups with 5 minutes delay between each and print the results
    for i in range(35):
        result = await backup_ops.handle_backup_active("custom_id", "chat_bot", "lang", messages)
        print(f"Backup {i+1}: {result['backup_file']}")
        await asyncio.sleep(300)  # Wait for 5 minutes (300 seconds)

# Run the simulation
asyncio.run(simulate_backup())
