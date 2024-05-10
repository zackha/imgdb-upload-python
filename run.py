import os
import requests
from tqdm import tqdm
import pandas as pd

def list_images(directory):
    extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    return [os.path.join(root, file) 
            for root, _, files in os.walk(directory) 
            for file in files 
            if file.lower().endswith(extensions)]

def upload_image(image_path, api_key):
    url = "https://api.imgbb.com/1/upload"
    try:
        with open(image_path, "rb") as file:
            files = {"image": file}
            params = {"key": api_key}
            response = requests.post(url, files=files, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def process_images(directory, api_key):
    image_paths = list_images(directory)
    results = []

    for image_path in tqdm(image_paths, desc="Uploading images", unit="image"):
        result = upload_image(image_path, api_key)
        results.append(result)
        # Save results to Excel after each upload
        pd.json_normalize(results).to_excel("upload_results.xlsx", index=False)

if __name__ == "__main__":
    DIRECTORY = "/path/to/your/images"
    API_KEY = "your_imgbb_api_key"
    process_images(DIRECTORY, API_KEY)
