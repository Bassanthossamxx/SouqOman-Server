from django.conf import settings
from imagekitio import ImageKit

imagekit = ImageKit(
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT,
)

def upload_image_to_imagekit(file_obj, filename):
    try:
        upload = imagekit.upload(file=file_obj, file_name=filename)
        return upload.get("url")
    except Exception as e:
        print("Image upload failed:", e)
        return None
