import boto3
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

DO_SPACES_REGION = os.getenv('DO_SPACES_REGION')
DO_SPACES_ENDPOINT = os.getenv('DO_SPACES_ENDPOINT')
DO_SPACES_ACCESS_KEY = os.getenv('DO_SPACES_ACCESS_KEY')
DO_SPACES_SECRET_KEY = os.getenv('DO_SPACES_SECRET_KEY')

# Log environment variables
logging.debug(f"DO_SPACES_REGION: {DO_SPACES_REGION}")
logging.debug(f"DO_SPACES_ENDPOINT: {DO_SPACES_ENDPOINT}")
logging.debug(f"DO_SPACES_ACCESS_KEY: {DO_SPACES_ACCESS_KEY}")
logging.debug(f"DO_SPACES_SECRET_KEY: {DO_SPACES_SECRET_KEY}")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=DO_SPACES_REGION,
    endpoint_url=DO_SPACES_ENDPOINT,
    aws_access_key_id=DO_SPACES_ACCESS_KEY,
    aws_secret_access_key=DO_SPACES_SECRET_KEY
)

try:
    response = s3_client.list_buckets()
    print("Buckets:", response['Buckets'])
except Exception as e:
    logging.error("Error occurred", exc_info=True)
