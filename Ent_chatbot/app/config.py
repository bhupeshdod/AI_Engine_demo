import os
from dotenv import load_dotenv

load_dotenv()

DO_SPACES_REGION = os.getenv('DO_SPACES_REGION')
DO_SPACES_ENDPOINT = os.getenv('DO_SPACES_ENDPOINT')
DO_SPACES_ACCESS_KEY = os.getenv('DO_SPACES_ACCESS_KEY')
DO_SPACES_SECRET_KEY = os.getenv('DO_SPACES_SECRET_KEY')
BUCKET_NAME = 'entcb'

if not all([DO_SPACES_REGION, DO_SPACES_ACCESS_KEY, DO_SPACES_SECRET_KEY, BUCKET_NAME]):
    raise RuntimeError("Missing one or more DigitalOcean Spaces credentials or bucket name in environment variables")

print(DO_SPACES_ENDPOINT)