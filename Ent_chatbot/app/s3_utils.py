import boto3
from botocore.exceptions import ClientError
from io import BytesIO
import zipfile
from datetime import datetime
from app.config import DO_SPACES_REGION, DO_SPACES_ENDPOINT, DO_SPACES_ACCESS_KEY, DO_SPACES_SECRET_KEY, BUCKET_NAME

s3_client = boto3.client(
    's3',
    region_name=DO_SPACES_REGION,
    endpoint_url=DO_SPACES_ENDPOINT,
    aws_access_key_id=DO_SPACES_ACCESS_KEY,
    aws_secret_access_key=DO_SPACES_SECRET_KEY
)

async def check_folder_exists(bucket_name, folder_key):
    try:
        response = await s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_key, MaxKeys=1)
        return 'Contents' in response
    except ClientError as e:
        raise RuntimeError(f"ClientError while checking folder: {str(e)}")

async def create_folders(bucket_name, folders):
    results = []
    for folder in folders:
        if not await check_folder_exists(bucket_name, folder):
            await s3_client.put_object(Bucket=bucket_name, Key=folder)
            results.append({"folder": folder, "status": "created"})
        else:
            results.append({"folder": folder, "status": "already exists"})
    return results

async def list_files_in_folder(bucket_name, folder_key):
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=folder_key)

        files = []
        async for page in page_iterator:
            if 'Contents' in page:
                files.extend([content['Key'] for content in page['Contents'] if not content['Key'].endswith('/')])
        
        return files
    except ClientError as e:
        raise RuntimeError(f"ClientError while listing files: {str(e)}")

async def create_zip_from_files(bucket_name, files):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_key in files:
            file_obj = await s3_client.get_object(Bucket=bucket_name, Key=file_key)
            file_content = file_obj['Body'].read()
            zip_file.writestr(file_key.split('/')[-1], file_content)
    buffer.seek(0)
    return buffer

async def delete_files_in_folder(bucket_name, folder_key):
    files = await list_files_in_folder(bucket_name, folder_key)
    if files:
        objects_to_delete = [{'Key': file} for file in files]
        await s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})

async def extract_and_upload_zip(bucket_name, zip_file, destination_folder):
    with zipfile.ZipFile(zip_file) as zip_file:
        for file_name in zip_file.namelist():
            file_data = zip_file.read(file_name)
            await s3_client.put_object(Bucket=bucket_name, Key=f"{destination_folder}{file_name}", Body=file_data)

async def get_next_backup_number(bucket_name, seq_file_key):
    try:
        seq_file_obj = await s3_client.get_object(Bucket=bucket_name, Key=seq_file_key)
        seq_number = int(seq_file_obj['Body'].read().decode('utf-8').strip())
        next_seq_number = (seq_number % 30) + 1
    except ClientError:
        next_seq_number = 1
    except ValueError:
        next_seq_number = 1
    
    await s3_client.put_object(Bucket=bucket_name, Key=seq_file_key, Body=str(next_seq_number).zfill(2))
    return next_seq_number

async def update_backup_log(bucket_name, log_file_key, backup_file_name):
    log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {backup_file_name}\n"
    try:
        log_file_obj = await s3_client.get_object(Bucket=bucket_name, Key=log_file_key)
        log_content = log_file_obj['Body'].read().decode('utf-8')
    except ClientError:
        log_content = ""
    
    log_content += log_entry
    await s3_client.put_object(Bucket=bucket_name, Key=log_file_key, Body=log_content)
