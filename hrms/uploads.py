import cloudinary
import cloudinary.uploader
from django.conf import settings
from rest_framework import serializers


def upload_image(file_obj, folder=None):
    if not file_obj:
        raise serializers.ValidationError({"image": "No image file was provided."})

    if not all(
        [
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET,
        ]
    ):
        raise serializers.ValidationError({"image": "Cloudinary is not configured."})

    content_type = getattr(file_obj, "content_type", "")
    if content_type and not content_type.startswith("image/"):
        raise serializers.ValidationError({"image": "Uploaded file must be an image."})

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

    try:
        result = cloudinary.uploader.upload(
            file_obj,
            folder=folder or settings.CLOUDINARY_UPLOAD_FOLDER,
            resource_type="image",
        )
    except Exception as exc:
        raise serializers.ValidationError({"image": f"Image upload failed: {exc}"}) from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise serializers.ValidationError({"image": "Cloudinary did not return an image URL."})
    return secure_url
