import requests
import os

SERVER_URL = "http://localhost:8998"
UPLOAD_IMAGE_ENDPOINT = f"{SERVER_URL}/upload-image/"
UPLOAD_VIDEO_ENDPOINT = f"{SERVER_URL}/upload-video/" # New endpoint
TEST_IMAGE_PATH = "image.png"
TEST_VIDEO_PATH = "video.mp4" # New test video file

# --- Helper to create dummy image (if not exists) ---
def create_dummy_image(path):
    if not os.path.exists(path):
        print(f"Creating dummy image at {path} for testing...")
        try:
            from PIL import Image
            img = Image.new('RGB', (60, 30), color = 'red')
            img.save(path)
            print("Dummy image created.")
        except ImportError:
            print("Pillow not installed. Cannot create dummy image. Please install it (pip install Pillow).")
            exit()
        except Exception as e:
            print(f"Could not create dummy image: {e}")
            exit()

# --- Helper to create dummy video (if not exists) ---
def create_dummy_video(path):
    if not os.path.exists(path):
        print(f"Creating dummy video at {path} for testing...")
        try:
            # Requires moviepy: pip install moviepy
            from moviepy.editor import ColorClip
            clip = ColorClip(size=(128, 72), color=(0, 0, 255), duration=2) # Small blue video, 2 seconds
            clip.write_videofile(path, fps=24, logger=None) # logger=None to suppress moviepy output
            print("Dummy video created.")
        except ImportError:
            print("moviepy not installed. Cannot create dummy video. Please install it (pip install moviepy).")
            # If moviepy is not installed, you'll need to manually place a video.mp4 file
            print(f"Please place a '{path}' file in the same directory to run video tests.")
            # Do not exit here, allow other tests to run if possible
        except Exception as e:
            print(f"Could not create dummy video: {e}")
            # Do not exit here, allow other tests to run if possible


def test_upload_image():
    """
    Tests the /upload-image/ endpoint.
    """
    create_dummy_image(TEST_IMAGE_PATH) # Ensure image exists before testing

    print(f"\n--- Attempting to upload image: {TEST_IMAGE_PATH} ---")

    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"Skipping image upload test: '{TEST_IMAGE_PATH}' not found.")
        return

    with open(TEST_IMAGE_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_IMAGE_PATH), f, "image/png")} # Adjust mime type if needed (e.g., image/jpeg)

        try:
            response = requests.post(UPLOAD_IMAGE_ENDPOINT, files=files)

            print(f"Response Status Code: {response.status_code}")
            print(f"Response Body: {response.json()}")

            if response.status_code == 200:
                print("\nImage upload test successful!")
                response_data = response.json()
                print(f"Uploaded URL: {response_data.get('url')}")
                print(f"Public ID: {response_data.get('public_id')}")
            else:
                print("\nImage upload test failed.")

        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to the server at {SERVER_URL}.")
            print("Please ensure your FastAPI server is running.")
        except Exception as e:
            print(f"An unexpected error occurred during image upload: {e}")

def test_upload_video():
    """
    Tests the /upload-video/ endpoint.
    """
    create_dummy_video(TEST_VIDEO_PATH) # Ensure video exists before testing

    print(f"\n--- Attempting to upload video: {TEST_VIDEO_PATH} ---")

    if not os.path.exists(TEST_VIDEO_PATH):
        print(f"Skipping video upload test: '{TEST_VIDEO_PATH}' not found.")
        return

    with open(TEST_VIDEO_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_VIDEO_PATH), f, "video/mp4")} # Adjust mime type if needed (e.g., video/quicktime)

        try:
            response = requests.post(UPLOAD_VIDEO_ENDPOINT, files=files)

            print(f"Response Status Code: {response.status_code}")
            print(f"Response Body: {response.json()}")

            if response.status_code == 200:
                print("\nVideo upload test successful!")
                response_data = response.json()
                print(f"Uploaded URL: {response_data.get('url')}")
                print(f"Public ID: {response_data.get('public_id')}")
            else:
                print("\nVideo upload test failed.")

        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to the server at {SERVER_URL}.")
            print("Please ensure your FastAPI server is running.")
        except Exception as e:
            print(f"An unexpected error occurred during video upload: {e}")


if __name__ == "__main__":
    print("Starting server tests...")
    # test_upload_image()
    test_upload_video() # Call the new video test
    print("\nTests finished.")