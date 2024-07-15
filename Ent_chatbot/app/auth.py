import json
from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.s3_utils import s3_client, BUCKET_NAME

async def validate_client_keys(access_key: str, secret_key: str):
    clients_data = await read_clients_file()
    if access_key in clients_data and clients_data[access_key]['secret_key'] == secret_key:
        return True
    return False

async def validate_golden_key(provided_key):
    try:
        golden_key_obj = await s3_client.get_object(Bucket=BUCKET_NAME, Key='golden_key.txt')
        golden_key = golden_key_obj['Body'].read().decode('utf-8').strip()
        return provided_key == golden_key
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"ClientError while validating golden key: {str(e)}")

async def read_clients_file():
    try:
        clients_obj = await s3_client.get_object(Bucket=BUCKET_NAME, Key='clients.json')
        clients_data = json.loads(clients_obj['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            clients_data = {}
        else:
            raise HTTPException(status_code=500, detail=f"ClientError while reading clients file: {str(e)}")
    return clients_data

async def update_clients_file(clients_data):
    try:
        clients_content = json.dumps(clients_data, indent=4)
        await s3_client.put_object(Bucket=BUCKET_NAME, Key='clients.json', Body=clients_content)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"ClientError while updating clients file: {str(e)}")
