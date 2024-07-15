from fastapi import APIRouter, HTTPException, Header
import json
import hashlib
import uuid
from models import Client
from utils import load_messages, load_keys
import os

auth_router = APIRouter()
messages = load_messages()
keys = load_keys()


class AuthService:
    GOLDEN_KEY = keys["golden_key"]

    @staticmethod
    def validate_golden_key(x_golden_key: str = Header(...)):
        if x_golden_key != AuthService.GOLDEN_KEY:
            raise HTTPException(
                status_code=403, detail=messages["invalid_golden_key"])

    @staticmethod
    def authenticate(secret_key: str = Header(...), access_key: str = Header(...)):
        try:
            with open("clients.json", "r") as file:
                clients = json.load(file)
            for client in clients:
                if client["secret_key"] == secret_key and client["access_key"] == access_key:
                    return True
            raise HTTPException(
                status_code=403, detail=messages["invalid_credentials"])
        except FileNotFoundError:
            raise HTTPException(
                status_code=500, detail=messages["clients_file_not_found"])
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500, detail=messages["error_reading_clients_file"])


@auth_router.post("/create-client")
async def create_client(client: Client, x_golden_key: str = Header(...)):
    AuthService.validate_golden_key(x_golden_key)

    secret_key = uuid.uuid4().hex
    access_key = uuid.uuid4().hex

    hashed_secret_key = hashlib.sha256(secret_key.encode()).hexdigest()
    hashed_access_key = hashlib.sha256(access_key.encode()).hexdigest()

    client_data = {
        "client_name": client.client_name,
        "secret_key": hashed_secret_key,
        "access_key": hashed_access_key
    }

    file_path = "clients.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        data = []

    data.append(client_data)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    return {
        "client_name": client.client_name,
        "secret_key": hashed_secret_key,
        "access_key": hashed_access_key
    }
