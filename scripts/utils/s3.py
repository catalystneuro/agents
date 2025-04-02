import boto3
import os
from typing import List, Optional, Union
from pathlib import Path


def create_s3_client():
    """
    Create an S3 client using credentials from environment variables.

    Environment variables used:
    - AWS_ACCESS_KEY_ID: AWS access key
    - AWS_SECRET_ACCESS_KEY: AWS secret key
    - AWS_SESSION_TOKEN: AWS session token (optional)
    - AWS_REGION: AWS region (defaults to 'us-east-1')

    Returns:
        boto3.client: Configured S3 client
    """
    # Get credentials from environment variables
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-2')

    # Create and return the client with explicit credentials if provided
    if aws_access_key and aws_secret_key:
        return boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
    else:
        # Fall back to boto3's default credential resolution
        return boto3.client('s3', region_name=aws_region)


def list_s3_files(
    bucket_name: str = "llm-agents-data",
    prefix: str = "",
    recursive: bool = True
) -> List[str]:
    """
    List files from an S3 bucket/folder.

    Args:
        bucket_name: Name of the S3 bucket
        prefix: Folder path within the bucket (optional)
        recursive: Whether to list files recursively in subfolders

    Returns:
        List of file paths found in the bucket/folder
    """
    s3_client = create_s3_client()
    file_list = []

    # If not recursive and prefix doesn't end with '/', add it to list only direct children
    if not recursive and prefix and not prefix.endswith('/'):
        prefix = prefix + '/'

    paginator = s3_client.get_paginator('list_objects_v2')

    # Set delimiter to '/' if not recursive to only get files in the current directory
    delimiter = '/' if not recursive else None

    # Paginate through results
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter=delimiter):
        # Process files (Contents)
        if 'Contents' in page:
            for obj in page['Contents']:
                # Skip the directory itself if it's included in the results
                if obj['Key'] != prefix:
                    file_list.append(obj['Key'])

        # If not recursive, also include common prefixes (folders)
        if not recursive and 'CommonPrefixes' in page:
            for prefix_obj in page['CommonPrefixes']:
                file_list.append(prefix_obj['Prefix'])

    return file_list


def download_s3_files(
    bucket_name: str = "llm-agents-data",
    prefix: str = "",
    local_dir: Union[str, Path] = ".",
    recursive: bool = True,
    filter_pattern: Optional[str] = None
) -> List[Path]:
    """
    Download files from an S3 bucket/folder.

    Args:
        bucket_name: Name of the S3 bucket
        prefix: Folder path within the bucket (optional)
        local_dir: Local directory to save downloaded files
        recursive: Whether to download files recursively from subfolders
        filter_pattern: Optional pattern to filter files by name

    Returns:
        List of paths to the downloaded files
    """
    import re

    s3_client = create_s3_client()
    local_dir = Path(local_dir)
    local_dir.mkdir(exist_ok=True, parents=True)
    downloaded_files = []

    # Get list of files from S3
    files = list_s3_files(bucket_name, prefix, recursive)

    # Apply filter if provided
    if filter_pattern:
        pattern = re.compile(filter_pattern)
        files = [f for f in files if pattern.search(f)]

    # Download each file
    for s3_key in files:
        # Determine local file path, preserving directory structure
        if prefix:
            # If prefix is specified, remove it from the path to avoid duplicating folders
            rel_path = s3_key[len(prefix):] if s3_key.startswith(prefix) else s3_key
            rel_path = rel_path.lstrip('/')
        else:
            rel_path = s3_key

        local_file_path = local_dir / rel_path

        # Create parent directories if they don't exist
        local_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        s3_client.download_file(bucket_name, s3_key, str(local_file_path))
        downloaded_files.append(local_file_path)

    return downloaded_files
