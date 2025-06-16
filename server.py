import os
import shutil
import tempfile
import json
from typing import List, Optional
from image_url import upload_image_to_cloudinary # Keep this for image uploads
from video_url import upload_video_to_cloudinary # Import the new video upload function
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import datetime

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PUBLIC_IMAGES_DIR = "public_images"
PUBLIC_VIDEOS_DIR = "public_videos" # New directory for videos
IMAGE_METADATA_DIR = "image_metadata"
VIDEO_METADATA_DIR = "video_metadata" # New directory for video metadata

def save_metadata(filename: str, public_id: str, url: str, original_filename: str, metadata_dir: str):
    os.makedirs(metadata_dir, exist_ok=True)
    metadata_filename = f"{os.path.splitext(filename)[0]}.json"
    metadata_path = os.path.join(metadata_dir, metadata_filename)

    metadata_content = {
        "public_id": public_id,
        "url": url,
        "upload_time": datetime.datetime.now().isoformat(),
        "original_filename": original_filename
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata_content, f, indent=4)
    print(f"Metadata saved to: {metadata_path}")


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Media URL Convertor API. Visit /docs for API documentation."}

@app.post("/upload-image/")
async def upload_image_endpoint(
    file: UploadFile = File(...),
):
    local_file_path = None
    try:
        os.makedirs(PUBLIC_IMAGES_DIR, exist_ok=True)

        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        original_filename = file.filename

        new_filename_with_ext = f"{current_time}_{original_filename}"
        local_file_path = os.path.join(PUBLIC_IMAGES_DIR, new_filename_with_ext)

        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"Locally saved uploaded image file to: {local_file_path}")

        uploaded_url, public_id = upload_image_to_cloudinary(local_file_path)

        if uploaded_url and public_id:
            save_metadata(new_filename_with_ext, public_id, uploaded_url, original_filename, IMAGE_METADATA_DIR)

            return JSONResponse(status_code=200, content={
                "message": "Image uploaded successfully",
                "url": uploaded_url,
                "public_id": public_id,
                "local_path": local_file_path,
                "metadata_saved": True
            })
        else:
            raise HTTPException(status_code=500, detail="Cloudinary image upload failed: Check server logs for details.")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during image upload: {str(e)}")
    finally:
        if local_file_path and os.path.exists(local_file_path):
            os.remove(local_file_path)
            print(f"Cleaned up local image file: {local_file_path}")

@app.post("/upload-video/") # New endpoint for video uploads
async def upload_video_endpoint(
    file: UploadFile = File(...),
):
    local_file_path = None
    try:
        os.makedirs(PUBLIC_VIDEOS_DIR, exist_ok=True) # Ensure video directory exists

        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        original_filename = file.filename

        new_filename_with_ext = f"{current_time}_{original_filename}"
        local_file_path = os.path.join(PUBLIC_VIDEOS_DIR, new_filename_with_ext) # Save to video directory

        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"Locally saved uploaded video file to: {local_file_path}")

        uploaded_url, public_id = upload_video_to_cloudinary(local_file_path) # Use video upload function

        if uploaded_url and public_id:
            save_metadata(new_filename_with_ext, public_id, uploaded_url, original_filename, VIDEO_METADATA_DIR) # Save to video metadata directory

            return JSONResponse(status_code=200, content={
                "message": "Video uploaded successfully",
                "url": uploaded_url,
                "public_id": public_id,
                "local_path": local_file_path,
                "metadata_saved": True
            })
        else:
            raise HTTPException(status_code=500, detail="Cloudinary video upload failed: Check server logs for details.")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during video upload: {str(e)}")
    finally:
        if local_file_path and os.path.exists(local_file_path):
            os.remove(local_file_path)
            print(f"Cleaned up local video file: {local_file_path}")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8998, reload=True)