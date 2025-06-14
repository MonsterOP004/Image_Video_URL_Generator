import os
import shutil
import tempfile
from typing import List, Optional
from image_url import upload_image_to_cloudinary, delete_image, delete_images_by_tag, list_images_by_tag
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Cloudinary Image Management API (Modularized)",
    description="API for uploading, deleting, and listing images on Cloudinary, using functions from image_url.py."
)

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Cloudinary Image API. Visit /docs for API documentation."}

@app.post("/upload-image/")
async def upload_image_endpoint(
    file: UploadFile = File(...),
):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        print(f"Temporarily saved uploaded file to: {temp_file_path}")

        uploaded_url, public_id = upload_image_to_cloudinary(temp_file_path) # Call function from image_url.py

        if uploaded_url and public_id:
            return JSONResponse(status_code=200, content={
                "message": "Image uploaded successfully",
                "url": uploaded_url,
                "public_id": public_id,
            })
        else:
            raise HTTPException(status_code=500, detail="Cloudinary upload failed: Check server logs for details.")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during upload: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")


@app.delete("/delete-image/{public_id}")
async def delete_image_endpoint(public_id: str):
    try:
        success = delete_image(public_id) # Call function from image_url.py
        if success:
            return JSONResponse(status_code=200, content={"message": f"Image '{public_id}' deleted successfully."})
        else:
            raise HTTPException(status_code=404, detail=f"Image '{public_id}' not found or could not be deleted.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")

@app.delete("/delete-by-tag/{tag_name}")
async def delete_by_tag_endpoint(tag_name: str):
    try:
        success = delete_images_by_tag(tag_name) # Call function from image_url.py
        if success:
            return JSONResponse(status_code=200, content={"message": f"Deletion command sent for images tagged '{tag_name}'."})
        else:
            raise HTTPException(status_code=500, detail=f"Failed to initiate deletion for tag '{tag_name}'.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete images by tag: {str(e)}")

@app.get("/list-by-tag/{tag_name}")
async def list_by_tag_endpoint(tag_name: str):
    try:
        image_urls = list_images_by_tag(tag_name) # Call function from image_url.py
        if image_urls:
            return JSONResponse(status_code=200, content={"tag": tag_name, "image_urls": image_urls, "count": len(image_urls)})
        else:
            return JSONResponse(status_code=200, content={"tag": tag_name, "image_urls": [], "message": "No images found with this tag."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images by tag: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8998, reload=True)
