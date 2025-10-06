from django.conf import settings
from imagekitio import ImageKit

imagekit = ImageKit(
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT,
)

def upload_to_imagekit(file_obj, filename):
    """
    Upload image to ImageKit and return dict with url and fileId.

    Args:
        file_obj: File object to upload
        filename: Name for the uploaded file

    Returns:
        dict: {"url": str, "fileId": str} or None if upload fails
    """
    try:
        upload = imagekit.upload(file=file_obj, file_name=filename)
        return {
            "url": upload.get("url"),
            "fileId": upload.get("fileId")
        }
    except Exception as e:
        print(f"ImageKit upload failed for {filename}: {e}")
        return None
