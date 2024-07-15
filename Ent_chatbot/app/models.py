from pydantic import BaseModel

class CreateChatbotRequest(BaseModel):
    client_id: str
    chat_bot: str
    access_key: str
    secret_key: str

class AddLanguageRequest(BaseModel):
    lang: str
    client_id: str
    chat_bot: str
    access_key: str
    secret_key: str

class BackupActiveRequest(BaseModel):
    client_id: str
    chat_bot: str
    lang: str
    access_key: str
    secret_key: str

class UploadToChatbotActiveRequest(BaseModel):
    client_id: str
    chat_bot: str
    lang: str
    access_key: str
    secret_key: str

class RestoreActiveRequest(BaseModel):
    client_id: str
    chat_bot: str
    lang: str
    backup_file: str
    access_key: str
    secret_key: str

class CreateClientRequest(BaseModel):
    client_id: str
    golden_key: str

class ClientCredentials(BaseModel):
    access_key: str
    secret_key: str
