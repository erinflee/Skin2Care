# s3_utils.py
# -----------------------------------------------------------------------------
# Loads the FAISS index from Amazon S3 at app startup instead of committing the
# 41MB of binary index files to Git.
#
# Why this exists:
#   - index.faiss (29MB) and index.pkl (12MB) are binary artifacts. Binary blobs
#     don't belong in version control (they bloat history and can't be diffed),
#     so they live in an S3 bucket and get downloaded at runtime.
#   - The 195MB raw scrape archive also lives in the bucket, but the running app
#     never downloads it — which is why the app's IAM user is scoped to read
#     only the faiss_index/ prefix (least privilege).
#
# How it fits in:
#   app.py / ml.py call ensure_faiss_index() before FAISS.load_local(). If S3
#   isn't configured, it does nothing and the app uses whatever index is already
#   on local disk — so the project still runs for anyone without AWS.
#
# Config (read from environment variables, set in .env locally):
#   S3_BUCKET             - the bucket name        (required to enable S3)
#   AWS_REGION            - e.g. us-east-1
#   AWS_ACCESS_KEY_ID     - picked up automatically by boto3's credential chain
#   AWS_SECRET_ACCESS_KEY - picked up automatically by boto3's credential chain
# -----------------------------------------------------------------------------



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
            Filename=str(path)
        )
        
    return local_dir



def upload_faiss_index(local_dir="faiss_index"):
    if not s3_enabled():
        return local_dir

    bucket = os.environ["S3_BUCKET"]
    region_name = os.environ.get("AWS_REGION", "us-east-1")

    client = boto3.client("s3", region_name=region_name)

    for filename in INDEX_FILES:
        key = f"faiss_index/{filename}"
        path = Path(local_dir) / filename
        if not path.is_file():
            raise FileNotFoundError(f"{path} not found - run index_to_faiss() first")

        client.upload_file(
            Filename=str(path),
            Bucket=bucket,
            Key=key
        )
    
