
import os
import cloudinary
import cloudinary.uploader
from flask import current_app

def upload_image(file_obj, folder="profile_pics"):
    """
    Uploads an image to Cloudinary using credentials from app config.
    
    Args:
        file_obj: The file object to upload (e.g., from request.files['image'])
        folder: The folder in Cloudinary to upload to.

    Returns:
        str: The secure URL of the uploaded image.
    """
    
    # Cloudinary is now configured globally in app/__init__.py

    try:
        current_app.logger.info(f"Attempting Cloudinary upload to folder: {folder}")
        # Upload the file
        upload_result = cloudinary.uploader.upload(file_obj, folder=folder)
        
        url = upload_result.get('secure_url')
        current_app.logger.info(f"Upload successful. URL: {url}")
        return url
        
    except Exception as e:
        current_app.logger.error(f"Cloudinary Upload Failed: {str(e)}")
        print(f"DEBUG: Cloudinary Error: {str(e)}") # Print to console for visibility
        # Fallback to a placeholder in case of error
        return f"https://via.placeholder.com/150?text=Upload+Failed"

