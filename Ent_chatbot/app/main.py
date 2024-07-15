from fastapi import FastAPI
from app.endpoints import client
from app.endpoints import chatbot, backup, upload, restore

app = FastAPI()

app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
app.include_router(backup.router, prefix="/backup", tags=["backup"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(restore.router, prefix="/restore", tags=["restore"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)