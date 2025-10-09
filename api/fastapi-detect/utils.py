import asyncio
from fastapi import UploadFile, File, HTTPException, status
from sympy import det
from loggers import utillogger
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, ParamValidationError
from config import settings
from urllib.parse import quote


R2_ACCESS_KEY_ID = settings.r2_access_key_id
R2_SECRET_ACCESS_KEY = settings.r2_secret_access_key
R2_ENDPOINT = settings.r2_endpoint
R2_BUCKET = settings.r2_bucket


def upload_to_s3(file, R2_BUCKET, r2_key):
    s3_client = boto3.client(
    service_name='s3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name='auto',
    config=Config(signature_version='s3v4'))

    s3_client.upload_fileobj(file, R2_BUCKET, r2_key, ExtraArgs={'ACL': 'public-read'})
    

def get_file_url(file):
    
    utillogger.info('starting this function')

    
    r2_key = f"fastapi/uploads/{file.filename}"
    utillogger.info(r2_key)
    encoded_r2_key = quote(r2_key)
    utillogger.info(f'encoded r2key is {encoded_r2_key}')

    try:
        upload_to_s3(file.file, R2_BUCKET, r2_key)
    except ClientError as e:
        utillogger.error(f"AWS ClientError during upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file to S3, why? {e}")
    except ParamValidationError as e:
        utillogger.error(f"{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"something's up with your parameters buddy; which? {e}")


    file_name = file.filename
    file_url  = f"https://staging-static.test.com/{encoded_r2_key}"

    utillogger.info(f"Analyzing {file_name}")
    utillogger.info(f"URL: {file_url}")

    return file_url