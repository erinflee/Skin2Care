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


