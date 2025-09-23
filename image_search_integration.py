# imagesearchintegration.py
import os
import shutil
import requests
from urllib.parse import quote

class ImageSearchIntegration:
    def __init__(self, output_dir=".", api_key="YOUR_PIXABAY_API_KEY"):
        self.output_dir = output_dir
        self.api_key = api_key  # Pixabay API key
        self.base_url = "https://pixabay.com/api/"

    def search_and_download_image(self, topic):
        """
        Search for an image related to the topic using Pixabay API and download it.
        Returns the path to the downloaded image or None if failed.
        """
        try:
            # Encode the topic for the URL
            query = quote(topic)
            url = f"{self.base_url}?key={self.api_key}&q={query}&image_type=photo&per_page=3"
            
            # Make API request
            response = requests.get(url)  
            response.raise_for_status()  # Raise exception for bad status codes
            data = response.json()

            # Check if images are found
            if data.get("hits") and len(data["hits"]) > 0:
                image_url = data["hits"][0]["largeImageURL"]  # Get the first image
                image_response = requests.get(image_url, stream=True)
                image_response.raise_for_status()

                # Determine file extension
                ext = image_url.split(".")[-1].lower()
                if ext not in ["jpg", "jpeg", "png"]:
                    ext = "jpg"  # Default to jpg if unknown

                # Create destination path
                topic_clean = topic.replace(" ", "_").replace("/", "_")
                dest_filename = f"{topic_clean}_topic_image.{ext}"
                dest_path = os.path.join(self.output_dir, dest_filename)

                # Save the image
                with open(dest_path, "wb") as f:
                    shutil.copyfileobj(image_response.raw, f)
                print(f"Image downloaded to: {dest_path}")
                return dest_path
            else:
                print(f"No images found for topic: {topic}")
                return None

        except Exception as e:
            print(f"Error in image search: {e}")
            return None

    def copy_image_to_output(self, source_path, topic):
        """
        Copy a downloaded image to the output directory with proper naming.
        """
        try:
            if source_path and os.path.exists(source_path):
                # Get file extension from source
                _, ext = os.path.splitext(source_path)
                if not ext:
                    ext = ".png"  # Default extension
                
                # Create destination path
                topic_clean = topic.replace(" ", "_").replace("/", "_")
                dest_filename = f"{topic_clean}_topic_image{ext}"
                dest_path = os.path.join(self.output_dir, dest_filename)
                
                # Copy the file (or move if already in output_dir)
                shutil.copy2(source_path, dest_path)
                print(f"Image copied to: {dest_path}")
                return dest_path
            else:
                print("No valid source image path provided")
                return None
                
        except Exception as e:
            print(f"Error copying image: {e}")
            return None