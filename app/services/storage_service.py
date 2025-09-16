"""
Storage service for unified MinIO/S3 operations.
Provides file upload, download, and management functionality.
"""
import logging
import io
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from minio import Minio
from minio.error import S3Error

from app.config.settings import settings

logger = logging.getLogger(__name__)


class StorageService:
    """
    Unified storage service supporting both MinIO (local) and S3 (production).
    Automatically switches between MinIO and S3 based on environment.
    """
    
    def __init__(self):
        """
        Initialize storage service.
        Uses MinIO for local development and S3 for production.
        """
        self.client = None
        self.is_minio = False
        self.bucket_name = settings.storage_bucket
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Initialize storage client based on environment.
        Production: Uses S3 with EC2 IAM role or default credentials
        Local: Uses MinIO with explicit credentials
        """
        try:
            if settings.is_production:
                # Production: Use S3 with default credential chain
                self.client = boto3.client(
                    's3',
                    region_name=settings.aws_region
                )
                self.is_minio = False
                logger.info("Initialized S3 client for production")
            else:
                # Local: Use MinIO
                self.client = Minio(
                    settings.minio_endpoint,
                    access_key=settings.minio_access_key,
                    secret_key=settings.minio_secret_key,
                    secure=settings.minio_secure
                )
                self.is_minio = True
                logger.info("Initialized MinIO client for local development")
                
            # Ensure bucket exists
            self._ensure_bucket_exists()
            
        except Exception as e:
            logger.error(f"Error initializing storage client: {e}")
            self.client = None
    
    def _ensure_bucket_exists(self) -> None:
        """
        Ensure the storage bucket exists, create if it doesn't.
        """
        try:
            if self.is_minio:
                # MinIO
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                    logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                # S3
                try:
                    self.client.head_bucket(Bucket=self.bucket_name)
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        self.client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': settings.aws_region
                            } if settings.aws_region != 'us-east-1' else {}
                        )
                        logger.info(f"Created S3 bucket: {self.bucket_name}")
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
    
    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Upload file to storage.
        
        Args:
            file_data: File data to upload
            object_name: Name of the object in storage
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Storage client not initialized")
            return False
        
        try:
            if self.is_minio:
                # MinIO upload
                file_data.seek(0, 2)  # Seek to end
                file_size = file_data.tell()
                file_data.seek(0)  # Seek back to beginning
                
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    data=file_data,
                    length=file_size,
                    content_type=content_type,
                    metadata=metadata or {}
                )
            else:
                # S3 upload
                extra_args = {
                    'ContentType': content_type
                }
                if metadata:
                    extra_args['Metadata'] = metadata
                
                self.client.upload_fileobj(
                    file_data,
                    self.bucket_name,
                    object_name,
                    ExtraArgs=extra_args
                )
            
            logger.info(f"Successfully uploaded file: {object_name}")
            return True
            
        except (S3Error, ClientError) as e:
            logger.error(f"Error uploading file {object_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading file {object_name}: {e}")
            return False
    
    def download_file(self, object_name: str) -> Optional[bytes]:
        """
        Download file from storage.
        
        Args:
            object_name: Name of the object in storage
            
        Returns:
            File data as bytes or None if error
        """
        if not self.client:
            logger.error("Storage client not initialized")
            return None
        
        try:
            if self.is_minio:
                # MinIO download
                response = self.client.get_object(self.bucket_name, object_name)
                data = response.read()
                response.close()
                response.release_conn()
                return data
            else:
                # S3 download
                response = self.client.get_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
                return response['Body'].read()
                
        except (S3Error, ClientError) as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading file {object_name}: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            object_name: Name of the object in storage
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Storage client not initialized")
            return False
        
        try:
            if self.is_minio:
                # MinIO delete
                self.client.remove_object(self.bucket_name, object_name)
            else:
                # S3 delete
                self.client.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
            
            logger.info(f"Successfully deleted file: {object_name}")
            return True
            
        except (S3Error, ClientError) as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file {object_name}: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """
        List files in storage.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file information dictionaries
        """
        if not self.client:
            logger.error("Storage client not initialized")
            return []
        
        try:
            files = []
            
            if self.is_minio:
                # MinIO list
                objects = self.client.list_objects(
                    self.bucket_name,
                    prefix=prefix,
                    recursive=True
                )
                
                for obj in objects:
                    files.append({
                        'name': obj.object_name,
                        'size': obj.size,
                        'last_modified': obj.last_modified,
                        'etag': obj.etag
                    })
            else:
                # S3 list
                response = self.client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
                
                for obj in response.get('Contents', []):
                    files.append({
                        'name': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag']
                    })
            
            return files
            
        except (S3Error, ClientError) as e:
            logger.error(f"Error listing files: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing files: {e}")
            return []
    
    def file_exists(self, object_name: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            object_name: Name of the object in storage
            
        Returns:
            True if file exists, False otherwise
        """
        if not self.client:
            logger.error("Storage client not initialized")
            return False
        
        try:
            if self.is_minio:
                # MinIO check
                try:
                    self.client.stat_object(self.bucket_name, object_name)
                    return True
                except S3Error as e:
                    if e.code == 'NoSuchKey':
                        return False
                    raise
            else:
                # S3 check
                try:
                    self.client.head_object(
                        Bucket=self.bucket_name,
                        Key=object_name
                    )
                    return True
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        return False
                    raise
                    
        except Exception as e:
            logger.error(f"Error checking file existence {object_name}: {e}")
            return False
    
    def generate_presigned_url(
        self,
        object_name: str,
        expiration: int = 3600,
        method: str = "GET"
    ) -> Optional[str]:
        """
        Generate presigned URL for file access.
        
        Args:
            object_name: Name of the object in storage
            expiration: URL expiration time in seconds
            method: HTTP method (GET, PUT, etc.)
            
        Returns:
            Presigned URL or None if error
        """
        if not self.client:
            logger.error("Storage client not initialized")
            return None
        
        try:
            if self.is_minio:
                # MinIO presigned URL
                if method.upper() == "GET":
                    return self.client.presigned_get_object(
                        self.bucket_name,
                        object_name,
                        expires=timedelta(seconds=expiration)
                    )
                elif method.upper() == "PUT":
                    return self.client.presigned_put_object(
                        self.bucket_name,
                        object_name,
                        expires=timedelta(seconds=expiration)
                    )
            else:
                # S3 presigned URL
                return self.client.generate_presigned_url(
                    f'{method.lower()}_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': object_name
                    },
                    ExpiresIn=expiration
                )
                
        except Exception as e:
            logger.error(f"Error generating presigned URL for {object_name}: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if storage service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        return self.client is not None 