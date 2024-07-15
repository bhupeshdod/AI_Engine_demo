from fastapi import FastAPI
from s3op import s3op_router
from auth import auth_router
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

app.include_router(s3op_router, prefix="/s3op", tags=["S3 Operations"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
