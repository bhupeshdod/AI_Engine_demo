from pydantic import BaseModel


class CreateChatbotRequest(BaseModel):
    custom_id: str
    chat_bot: str


class AddLanguageRequest(BaseModel):
    lang: str
    custom_id: str
    chat_bot: str


class Client(BaseModel):
    client_name: str
