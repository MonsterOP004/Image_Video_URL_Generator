import os
import shutil
import tempfile
import json
from typing import List, Optional
from image_url import upload_image_to_cloudinary
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import datetime

app = FastAPI()

PUBLIC_IMAGES_DIR = "public_images"
IMAGE_METADATA_DIR = "image_metadata" 

def save_image_metadata(filename: str, public_id: str, url: str, original_filename: str):

    os.makedirs(IMAGE_METADATA_DIR, exist_ok=True) # Ensure metadata directory exists
    metadata_filename = f"{os.path.splitext(filename)[0]}.json" # Use the timestamped filename base
    metadata_path = os.path.join(IMAGE_METADATA_DIR, metadata_filename)

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
    return {"message": "Welcome to the Image URL Convertor API. Visit /docs for API documentation."}

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

        print(f"Locally saved uploaded file to: {local_file_path}")

        uploaded_url, public_id = upload_image_to_cloudinary(local_file_path) 

        if uploaded_url and public_id:

            save_image_metadata(new_filename_with_ext, public_id, uploaded_url, original_filename)

            return JSONResponse(status_code=200, content={
                "message": "Image uploaded successfully",
                "url": uploaded_url,
                "public_id": public_id,
                "local_path": local_file_path,
                "metadata_saved": True
            })
        else:
            raise HTTPException(status_code=500, detail="Cloudinary upload failed: Check server logs for details.")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during upload: {str(e)}")
    finally:
        # The finally block will always clean up the local image file after processing.
        if local_file_path and os.path.exists(local_file_path):
            os.remove(local_file_path)
            print(f"Cleaned up local image file: {local_file_path}")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8998, reload=True)