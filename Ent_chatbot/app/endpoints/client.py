from fastapi import APIRouter, HTTPException
import uuid
from app.models import CreateClientRequest
from app.auth import read_clients_file, update_clients_file
from app.s3_utils import s3_client, BUCKET_NAME

router = APIRouter()

async def generate_and_store_golden_key():
    golden_key = str(uuid.uuid4())
    await s3_client.put_object(Bucket=BUCKET_NAME, Key='golden_key.txt', Body=golden_key)
    return golden_key

@router.post("/create_client")
async def create_client(request: CreateClientRequest):
    try:
        # Check if the golden key exists, if not create it
        try:
            golden_key_obj = await s3_client.get_object(Bucket=BUCKET_NAME, Key='golden_key.txt')
            golden_key = golden_key_obj['Body'].read().decode('utf-8').strip()
        except s3_client.exceptions.NoSuchKey:
            golden_key = await generate_and_store_golden_key()
            print(f"Generated new golden key: {golden_key}")
        
        if request.golden_key != golden_key:
            raise HTTPException(status_code=401, detail="Invalid golden key")

        clients_data = await read_clients_file()
        if request.client_id in [client['client_id'] for client in clients_data.values()]:
            raise HTTPException(status_code=400, detail=f"Client ID '{request.client_id}' already exists")

        access_key, secret_key = str(uuid.uuid4()), str(uuid.uuid4())

        clients_data[access_key] = {
            "client_id": request.client_id,
            "secret_key": secret_key
        }
        await update_clients_file(clients_data)

        return {
            "message": "Client created successfully",
            "access_key": access_key,
            "secret_key": secret_key
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
