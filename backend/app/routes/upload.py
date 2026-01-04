import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.config import Config

upload_bp = Blueprint("upload", __name__)

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secure=True,
)

@upload_bp.route("/", methods=["POST"])
@jwt_required()
def upload_image():
    """
    Accepts multipart/form-data with 'file' field.
    Returns Cloudinary secure URL.
    """
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    result = cloudinary.uploader.upload(file, folder="hr_system")
    return jsonify({"url": result.get("secure_url")}), 201
