import logging
import os
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from langchain_community.retrievers import ArxivRetriever
from langchain_community.tools import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from passlib.context import CryptContext

from backend.config import settings

BASE_RESOURCES_PATH = os.path.join("resources")
SRC_AUDIO_RESOURCES_PATH = os.path.join(BASE_RESOURCES_PATH, "src_audio")
TRANSCRIPTIONS_RESOURCES_PATH = os.path.join(BASE_RESOURCES_PATH, "transcriptions")


logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_resource_dirs():
    os.makedirs(SRC_AUDIO_RESOURCES_PATH, exist_ok=True)
    os.makedirs(TRANSCRIPTIONS_RESOURCES_PATH, exist_ok=True)



def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

def load_s3_bucket():
    bucket = os.environ.get("AWS_S3_BUCKET")
    if bucket:
        return bucket
    raise ValueError("Missing AWS S3 Bucket")


def fetch_file_from_s3(key: str, dest_filename: str | None):
    s3_client = get_s3_client()

    filename = (
        os.path.basename(key)
        if not dest_filename
        else f"{dest_filename}{os.path.splitext(key)[1]}"
    )
    local_filepath = os.path.join(CACHED_RESOURCES_PATH, filename)
    # Check locally before downloading
    if os.path.exists(local_filepath):
        return local_filepath
    else:
        try:
            _ = s3_client.head_object(Bucket=load_s3_bucket(), Key=key)
            s3_client.download_file(load_s3_bucket(), key, local_filepath)
            logger.info(f"Downloaded file {key} from S3")
            return local_filepath
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":  # File not found
                logger.error(f"File {key} not found on S3")
                return False
            else:
                logger.error("")
                return False


@lru_cache
def get_pinecone_vector_store():
    embeddings = OpenAIEmbeddings(model=settings.OPENAI_EMBEDDINGS_MODEL)
    return PineconeVectorStore(index=settings.PINECONE_INDEX_NAME, embedding=embeddings)


def get_tavily_web_search_tool():
    os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY
    return TavilySearchResults(max_results=5, search_depth="advanced", include_answer=True)


async def write_audio_to_file(contents: UploadFile, filename: str):
    file_path = os.path.join(SRC_AUDIO_RESOURCES_PATH, filename + ".audio")
    with open(file_path, "wb") as f:
        audio_data = await contents.read()
        f.write(audio_data)
    return file_path


async def write_transcription_to_file(contents: str, filename: str):
    file_path = os.path.join(TRANSCRIPTIONS_RESOURCES_PATH, filename + ".txt")
    with open(file_path, "wb") as f:
        f.write(contents.encode("utf-8"))
    return file_path
