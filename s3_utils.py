# s3_utils.py
# -----------------------------------------------------------------------------
# Loads the FAISS index from Amazon S3 at app startup instead of committing the
# 41MB of binary index files to Git.
#


import os
import boto3
from pathlib import Path

INDEX_FILES = ("index.faiss", "index.pkl")


def s3_enabled():
    """Return True when an S3 bucket is configured, False otherwise.

    When False, the caller should just use the local faiss_index/ folder.
    """
    bucket = os.environ.get("S3_BUCKET")
    return bool(bucket)


def ensure_faiss_index(local_dir="faiss_index"):
    """Make sure the FAISS index exists locally, downloading it from S3 when
    configured and not already cached. Return local_dir so the caller can pass
    it straight to FAISS.load_local().
    """
    if not s3_enabled():
        return local_dir

    bucket = os.environ["S3_BUCKET"]
    region_name = os.environ.get("AWS_REGION", "us-east-1")

    client = boto3.client("s3", region_name=region_name)
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    for filename in INDEX_FILES:
        key = f"faiss_index/{filename}"
        path = Path(local_dir) / filename
        if path.is_file():
            continue

        client.download_file(
            Bucket=bucket, 
            Key=key, 
            Filename=str(path))
        
    return local_dir





    
