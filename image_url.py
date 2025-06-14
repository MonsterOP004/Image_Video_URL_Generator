import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
import datetime
import pytz
from PIL import Image

load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv('CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('API_KEY')
CLOUDINARY_API_SECRET = os.getenv('API_SECRET')

# CLOUDINARY_URL = "CLOUDINARY_URL=cloudinary://<your_api_key>:<your_api_secret>@dxqqdr2te"

cloudinary.config(
  cloud_name = CLOUDINARY_CLOUD_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET
)

def upload_image_to_cloudinary(image_path: str) -> tuple[str | None, str | None]:
    try:
        folder = "public_images"
        current_time_utc = datetime.datetime.now(pytz.utc)
        tag_timestamp = current_time_utc.strftime("%Y%m%d_%H%M%S")
        tags = ["linkedin_content_gen", "temporary", f"upload_time_{tag_timestamp}"]

        upload_result = cloudinary.uploader.upload(
            image_path,
            folder=folder,
            tags = tags,
            overwrite=False
        )

        if upload_result and 'secure_url' in upload_result and 'public_id' in upload_result:
            secure_url = upload_result['secure_url']
            public_id = upload_result['public_id']
            print(f"Upload successful. Public ID: {public_id}")
            return secure_url, public_id
        else:
            print(f"Cloudinary upload failed for {image_path}. Result: {upload_result}")
            return None, None

    except cloudinary.exceptions.Error as e:
        print(f"Cloudinary Error: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during upload: {e}")
        return None, None


def delete_image(public_id: str):
    try:

        delete_result = cloudinary.uploader.destroy(public_id)
        if delete_result and delete_result.get('result') == 'ok':
            return True
        else:
            print(f"Cloudinary deletion failed for {public_id}. Result: {delete_result}")
            return False
        
    except cloudinary.exceptions.Error as e:
        print(f"Cloudinary Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def delete_images_by_tag(tag_name: str) -> bool:
   
    print(f"\n--- WARNING: Initiating deletion of all images with tag: '{tag_name}' ---")
    confirm = input("Are you absolutely sure you want to proceed? This action is irreversible. Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("Deletion cancelled by user.")
        return False

    try:
        result = cloudinary.api.delete_resources_by_tag(tag_name)

        if result and result.get('deleted'):
            print(f"Successfully sent delete command for tag '{tag_name}'. Deleted items: {result.get('deleted')}")
            return True
        else:
            print(f"Deletion command failed or no resources matched the tag '{tag_name}'. Result: {result}")
            return False

    except cloudinary.exceptions.Error as e:
        print(f"Cloudinary API Error during deletion by tag: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during deletion: {e}")
        return False

# --- Function to List All Image Links ---
def list_images_by_tag(tag_name: str) -> list[str]:
    tagged_urls = []
    next_cursor = None
    print(f"\n--- Fetching image URLs with tag: '{tag_name}' ---")
    try:
        while True:
            result = cloudinary.api.resources_by_tag(
                tag_name,
                type="upload",
                resource_type="image",
                max_results=500,
                next_cursor=next_cursor
            )
            resources = result.get('resources', [])
            for resource in resources:
                if 'secure_url' in resource:
                    tagged_urls.append(resource['secure_url'])
            next_cursor = result.get('next_cursor')
            if not next_cursor:
                break
            print(f"  Fetched {len(resources)} images for tag '{tag_name}'. Total so far: {len(tagged_urls)}. Fetching next page...")
        print(f"\n--- Finished fetching. Found a total of {len(tagged_urls)} URLs with tag '{tag_name}'. ---")
        return tagged_urls
    except cloudinary.exceptions.Error as e:
        print(f"Cloudinary API Error while listing by tag: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while listing by tag: {e}")
        return []


# <----------------------Test---------------------->

if __name__ == "__main__":
    test_image_path = "test_upload_image.png"
    # Ensure this tag is unique for your testing to avoid unintended deletions
    test_tag = "my_temp_test_tag_20250614" 
    
    while True:
        print("\n" + "="*40)
        print("  Cloudinary Operations Test Menu")
        print("="*40)
        print("1. Upload a test image")
        print("2. Delete a specific image by Public ID")
        print("3. Delete all images by Tag")
        print("4. List image URLs by Tag")
        print("0. Exit")
        print("="*40)

        choice = input("Enter your choice: ")

        if choice == '1':
            # Option 1: Upload Image
            img_path = input("Enter the path to the image you want to upload (e.g.,'test_upload_image.png'): ")

            if img_path:
                uploaded_url, public_id = upload_image_to_cloudinary(img_path)

                if uploaded_url and public_id:
                    print(f"\nUpload successful!")
                    print(f"  URL: {uploaded_url}")
                    print(f"  Public ID: {public_id}")
                else:
                    print("\nImage upload failed.")
            else:
                print("Skipping upload as dummy image could not be created.")

        elif choice == '2':
            # Option 2: Delete Specific Image by Public ID
            public_id_to_delete = input("Enter the Public ID of the image to delete (e.g., 'my_folder/my_image_abc123'): ")
            if public_id_to_delete:
                result = delete_image(public_id_to_delete)
                if result == True:
                    print(f"\nImage with Public ID '{public_id_to_delete}' deleted successfully.")
                else:
                    print(f"\nDeletion failed for image with Public ID '{public_id_to_delete}'.")
            else:
                print("No Public ID provided.")

        elif choice == '3':
            # Option 3: Delete All Images by Tag
            tag_to_delete_all = input("Enter the TAG name of images to delete (e.g., 'my_temp_test_tag_20250614'): ")
            if tag_to_delete_all:
                delete_images_by_tag(tag_to_delete_all)
            else:
                print("No tag provided.")

        elif choice == '4':
            # Option 4: List Image URLs by Tag
            tag_to_list = input("Enter the TAG name of images to list (e.g., 'my_temp_test_tag_20250614'): ")
            if tag_to_list:
                tagged_links = list_images_by_tag(tag_to_list)
                if tagged_links:
                    print(f"\n--- Images Tagged with '{tag_to_list}' ---")
                    for i, link in enumerate(tagged_links):
                        print(f"{i+1}. {link}")
                else:
                    print(f"No images found with tag '{tag_to_list}'.")
            else:
                print("No tag provided.")

        elif choice == '0':
            print("Exiting test menu. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")







