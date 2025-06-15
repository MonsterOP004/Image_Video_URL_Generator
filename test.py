import requests
import os

SERVER_URL = "http://localhost:8998" 
UPLOAD_ENDPOINT = f"{SERVER_URL}/upload-image/"
TEST_IMAGE_PATH = "image.png"

# Ensure the test image exists
if not os.path.exists(TEST_IMAGE_PATH):
    print(f"Error: Test image '{TEST_IMAGE_PATH}' not found.")
    print("Please create one using the 'create_dummy_image.py' script or provide a valid path to an existing image.")
    exit()

def test_upload_image():
    """
    Tests the /upload-image/ endpoint.
    """
    print(f"Attempting to upload image: {TEST_IMAGE_PATH}")

    with open(TEST_IMAGE_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_IMAGE_PATH), f, "image/png")} # Adjust mime type if needed (e.g., image/jpeg)
        # For a real image like .jpg, change "image/png" to "image/jpeg"

        try:
            response = requests.post(UPLOAD_ENDPOINT, files=files)

            print(f"Response Status Code: {response.status_code}")
            print(f"Response Body: {response.json()}")

            if response.status_code == 200:
                print("\nImage upload test successful!")
                response_data = response.json()
                print(f"Uploaded URL: {response_data.get('url')}")
                print(f"Public ID: {response_data.get('public_id')}")
                print(f"Local Path (from server response): {response_data.get('local_path')}")
            else:
                print("\nImage upload test failed.")

        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to the server at {SERVER_URL}.")
            print("Please ensure your FastAPI server is running.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("Starting server tests...")
    test_upload_image()
    print("Tests finished.")