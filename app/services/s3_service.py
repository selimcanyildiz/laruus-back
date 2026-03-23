import boto3
import uuid
from app.core.settings import config


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_REGION,
    )


def upload_file(file, folder: str, filename: str = None) -> dict:
    """S3'e dosya yükle, URL ve boyut döndür."""
    s3 = get_s3_client()
    ext = filename.rsplit(".", 1)[-1] if filename else "bin"
    key = f"{folder}/{uuid.uuid4().hex}.{ext}"

    s3.upload_fileobj(
        file,
        config.AWS_S3_BUCKET,
        key,
        ExtraArgs={"ContentType": _guess_content_type(ext)},
    )

    url = f"https://{config.AWS_S3_BUCKET}.s3.{config.AWS_REGION}.amazonaws.com/{key}"
    return {"url": url, "key": key}


def delete_file(key: str):
    """S3'ten dosya sil."""
    s3 = get_s3_client()
    s3.delete_object(Bucket=config.AWS_S3_BUCKET, Key=key)


def _guess_content_type(ext: str) -> str:
    types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
        "rar": "application/x-rar-compressed",
        "zip": "application/zip",
        "7z": "application/x-7z-compressed",
        "obj": "application/octet-stream",
        "fbx": "application/octet-stream",
        "glb": "model/gltf-binary",
        "gltf": "model/gltf+json",
    }
    return types.get(ext.lower(), "application/octet-stream")
