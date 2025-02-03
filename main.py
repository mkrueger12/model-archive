import os
from huggingface_hub import hf_hub_download, list_repo_files
import boto3
from tqdm import tqdm

# Configure these variables
REPO_ID = "deepseek-ai/DeepSeek-R1"  # e.g., "facebook/bart-large"
BUCKET_NAME = os.environ.get("BUCKET_NAME")  # e.g., "my-bucket"
S3_PREFIX = f"{REPO_ID}" # Optional: folder structure in S3
HF_TOKEN = None  # Set this if you need to access a private repository

def download_and_upload_to_s3():
    # Initialize S3 client
    s3_client = boto3.client('s3', endpoint_url='https://fly.storage.tigris.dev')

    # List all files in the repository
    files = list_repo_files(REPO_ID, token=HF_TOKEN)

    print(f"Starting download and upload for {REPO_ID}")

    # Download and upload each file
    for file in tqdm(files, desc="Processing files"):
        try:
            # Create local download path
            local_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=file,
                token=HF_TOKEN,
                local_files_only=False
            )

            # Create S3 key with prefix if provided
            s3_key = os.path.join(S3_PREFIX, file) if S3_PREFIX else file

            # Upload to S3
            s3_client.upload_file(
                local_path,
                BUCKET_NAME,
                s3_key
            )

            # Remove local file after upload
            os.remove(local_path)

        except Exception as e:
            print(f"Error processing {file}: {str(e)}")

if __name__ == "__main__":
    download_and_upload_to_s3()