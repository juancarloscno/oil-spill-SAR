from src.utils.definitions import UNPROCESSED_DATA_DIR
from src.utils.miscellaneous import download_url, extract_all_files
from dotenv import find_dotenv, load_dotenv
import os


def download_mklab_dataset():
    """Download the dataset from the MKLab website and extract it."""
    # Find the .env automatically by walking up directories until it's found
    load_dotenv(find_dotenv())
    # Download the dataset
    out_dir = os.path.join(UNPROCESSED_DATA_DIR, "mklab")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    print("Oil Spill Detection Dataset will be downloaded to: {}".format(out_dir))
    filename = download_url(os.getenv("MKLAB_DATASET_URL"), out_dir)
    # Extract the dataset
    filepath = os.path.join(out_dir, filename)
    extract_all_files(filepath, out_dir)
    # Delete the zip file
    os.remove(filepath)
    # Move all subfolders of the mklab dataset directory to one level upper
    print("Re-ordering dataset files...")
    for folder in os.listdir(out_dir):
        if os.path.isdir(os.path.join(out_dir, folder)):
            for file in os.listdir(os.path.join(out_dir, folder)):
                os.rename(
                    os.path.join(out_dir, folder, file), os.path.join(out_dir, file)
                )
            os.rmdir(os.path.join(out_dir, folder))
    print("Dataset has been downloaded and extracted successfully!")
