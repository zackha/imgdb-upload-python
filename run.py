import os
import requests
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_image_files(directory, extensions=('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
    """Returns a list of image file paths from the given directory and subdirectories."""
    return [os.path.join(root, file) 
            for root, _, files in os.walk(directory) 
            for file in files 
            if file.lower().endswith(extensions)]

def upload_to_imgbb(image_path, api_key):
    """Uploads an image to ImgBB and returns the JSON response or an error."""
    url = "https://api.imgbb.com/1/upload"
    try:
        with open(image_path, "rb") as file:
            files = {"image": file}
            params = {"key": api_key}
            response = requests.post(url, files=files, params=params)
        response.raise_for_status()
        return {"filename": os.path.basename(image_path), "response": response.json()}
    except requests.RequestException as e:
        return {"filename": os.path.basename(image_path), "error": str(e)}

def process_and_upload_images(directory, api_key, save_interval=10):
    """Processes image files in the given directory and uploads them to ImgBB."""
    image_paths = get_image_files(directory)
    results = []
    
    with ThreadPoolExecutor() as executor:
        future_to_image = {executor.submit(upload_to_imgbb, path, api_key): path for path in image_paths}
        
        for i, future in enumerate(tqdm(as_completed(future_to_image), total=len(future_to_image), desc="Uploading images", unit="image"), 1):
            result = future.result()
            results.append(result)
            if i % save_interval == 0:
                save_results_to_excel(results)
    
    # Final save for any remaining results
    save_results_to_excel(results)

def save_results_to_excel(results):
    """Saves the upload results to an Excel file."""
    df = pd.json_normalize(results)
    df.to_excel("upload_results.xlsx", index=False)

if __name__ == "__main__":
    DIRECTORY = "/path/to/your/images"
    API_KEY = "your_imgbb_api_key"
    process_and_upload_images(DIRECTORY, API_KEY)
