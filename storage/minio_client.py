from minio import Minio
from minio.error import S3Error
import os

class MinioClient:
    def __init__(self):
        self.client = Minio(
            os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "admin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "admin123"),
            secure=False
        )

    def ensure_bucket(self, bucket_name: str):
        """
        Crea el bucket si no existe.
        """
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        """
        Sube un archivo a MinIO.
        """
        self.ensure_bucket(bucket_name)

        try:
            self.client.fput_object(bucket_name, object_name, file_path)
            return {"message": "Archivo subido correctamente", "bucket": bucket_name, "object": object_name}
        except S3Error as e:
            return {"error": str(e)}

    def download_file(self, bucket_name: str, object_name: str, dest_path: str):
        """
        Descarga un archivo desde MinIO.
        """
        try:
            self.client.fget_object(bucket_name, object_name, dest_path)
            return {"message": "Archivo descargado correctamente", "dest": dest_path}
        except S3Error as e:
            return {"error": str(e)}

    def list_objects(self, bucket_name: str):
        """
        Lista objetos dentro de un bucket.
        """
        try:
            objects = self.client.list_objects(bucket_name)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            return {"error": str(e)}
