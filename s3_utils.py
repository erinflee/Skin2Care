# s3_utils.py
# -----------------------------------------------------------------------------
# Loads the FAISS index from Amazon S3 at app startup instead of committing the
# 41MB of binary index files to Git.
#
# 