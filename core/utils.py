from django.conf import settings
from imagekitio import ImageKit

imagekit = ImageKit(
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT,
)

def upload_to_imagekit(file_obj, filename=None):
    """
    Upload file_obj (InMemoryUploadedFile / UploadedFile) to ImageKit.
    Returns a dict: {"url": "...", "fileId": "..."} or None on failure.
    """
    try:
        fname = filename or getattr(file_obj, "name", "upload")
        resp = imagekit.upload(file=file_obj, file_name=fname)
        # response contains "url" and "fileId" (depending on ImageKit python client)
        return {
            "url": resp.get("url"),
            "fileId": resp.get("fileId") or resp.get("file_id")  # try both keys
        }
    except Exception as e:
        # you may want to log instead of print
        print("Image upload failed:", e)
        return None

def delete_from_imagekit(file_id):
    """
    Delete file by fileId (if available). Returns True on success, False otherwise.
    """
    if not file_id:
        return False
    try:
        imagekit.delete_file(file_id)
        return True
    except Exception as e:
        print("Image delete failed:", e)
        return False
