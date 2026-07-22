# s3_utils.py
# -----------------------------------------------------------------------------
# Loads the FAISS index from Amazon S3 at app startup instead of committing the
# 41MB of binary index files to Git.
#


import os
import boto3
from pathlib import Path

INDEX_FILES = ("index.faiss", "index.pkl")

