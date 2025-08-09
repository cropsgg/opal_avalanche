from __future__ import annotations

from typing import Tuple

from supabase import create_client, Client

from app.core.config import get_settings


def get_supabase() -> Client:
    s = get_settings()
    # Prefer full Supabase URL (project) + key
    if s.SUPABASE_URL and s.SUPABASE_SERVICE_KEY:
        return create_client(s.SUPABASE_URL, s.SUPABASE_SERVICE_KEY)
    if not (s.SUPABASE_STORAGE_URL and s.SUPABASE_SERVICE_KEY):
        raise RuntimeError("Supabase is not configured")
    return create_client(s.SUPABASE_STORAGE_URL, s.SUPABASE_SERVICE_KEY)


def get_signed_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    sb = get_supabase()
    res = sb.storage.from_(bucket).create_signed_url(path, expires_in)
    return res.get("signedURL")  # type: ignore[no-any-return]


def upload_bytes(bucket: str, path: str, data: bytes, content_type: str) -> Tuple[bool, str]:
    sb = get_supabase()
    res = sb.storage.from_(bucket).upload(path, data, {"content-type": content_type, "upsert": False})
    if isinstance(res, dict) and res.get("error"):
        return False, str(res["error"])  # type: ignore[index]
    return True, path


def upload_file(bucket: str, path: str, file_path: str, content_type: str = "application/octet-stream") -> Tuple[bool, str | None]:
    """Upload file to Supabase Storage"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        success, result = upload_bytes(bucket, path, data, content_type)
        if success:
            return True, None
        else:
            return False, result
    except Exception as e:
        return False, str(e)


def download_bytes(bucket: str, path: str) -> Tuple[bytes | None, str | None]:
    """Download bytes from Supabase storage. Returns (data, error)"""
    try:
        sb = get_supabase()
        data = sb.storage.from_(bucket).download(path)
        return data, None
    except Exception as e:
        return None, str(e)


