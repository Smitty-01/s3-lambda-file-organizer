
import json
import boto3
import os
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Process each S3 event record
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        # Skip if file is already in an organized folder
        if '/' in key and key.split('/')[0] in ['images', 'documents', 'videos', 'other']:
            print(f"File {key} is already organized, skipping")
            continue
        
        # Skip .gitkeep files used for folder structure
        if key.endswith('/.gitkeep'):
            print(f"Skipping folder placeholder file: {key}")
            continue
        
        # Determine file type based on extension
        file_extension = key.lower().split('.')[-1] if '.' in key else ''
        folder = get_folder_for_extension(file_extension)
        
        # Create new key with folder structure
        new_key = f"{folder}/{key}"
        
        try:
            # Copy object to new location
            s3_client.copy_object(
                Bucket=bucket,
                CopySource={'Bucket': bucket, 'Key': key},
                Key=new_key
            )
            
            # Delete original object
            s3_client.delete_object(Bucket=bucket, Key=key)
            
            print(f"Moved {key} to {new_key}")
            
        except Exception as e:
            print(f"Error moving {key}: {str(e)}")
            # Return error to trigger retry mechanism
            raise e

def get_folder_for_extension(extension):
    """Determine folder based on file extension"""
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg', 'webp']
    document_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx', 'csv']
    video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', 'm4v']
    
    if extension in image_extensions:
        return 'images'
    elif extension in document_extensions:
        return 'documents'
    elif extension in video_extensions:
        return 'videos'
    else:
        return 'other'

