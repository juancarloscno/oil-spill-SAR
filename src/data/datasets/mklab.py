from src.utils.definitions import UNPROCESSED_DATA_DIR
from src.utils.miscellaneous import download_url, extract_all_files
from dotenv import find_dotenv, load_dotenv
import os
import json


def from_mklab_to_coco_format(input_dir, output_dir, subset="train"):
    """Convert the Oil Spill Detection dataset owned by Multimedia Knowledge and Social Media Analytics Laboratory
    (MKLab) to COCO format.

    Args:
        input_dir (str): Path to the directory containing the MKLab dataset.
        output_dir (str): Path to the directory where the COCO dataset will be saved.
        subset (str): The subset of the dataset to convert. Can be 'train' or 'test'
    References:
        - Krestenitis, M., Orfanidis, G., Ioannidis, K., Avgerinakis, K., Vrochidis, S., & Kompatsiaris, I. (2019).
        Oil spill identification from satellite images using deep neural networks. Remote Sensing, 11(15), 1762.
        - Krestenitis, M., Orfanidis, G., Ioannidis, K., Avgerinakis, K., Vrochidis, S., & Kompatsiaris, I.
        (2019, January). Early Identification of Oil Spills in Satellite Images Using Deep CNNs.
        In International Conference on Multimedia Modeling (pp. 424-435). Springer, Cham.
    """
    supported_subsets = ["train", "test"]
    if subset not in supported_subsets:
        raise ValueError("The subset must be one of: {}".format(supported_subsets))
    # Create the output directory if it does not exist
    output_dir = os.path.join(output_dir, subset)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Create an empty COCO dataset specification
    coco_dataset = {
        "info": {
            "description": "Oil Spill Detection Dataset ({})".format(subset),
            "url": "https://m4d.iti.gr/oil-spill-detection-dataset/",
            "version": "1.0",
            "year": 2019,
            "contributor": "Multimedia Knowledge and Social Media Analytics Laboratory (MKLab)",
            "date_created": "2019/07/26",
        },
        # License non-commercial, use only for research purposes.
        "licenses": [
            {
                "id": 1,
                "name": "Non-Commercial",
                "url": "https://mklab.iti.gr/files/oli-spill-detection-terms.pdf",
            }
        ],
        "images": [],
        "annotations": [],
        "categories": [
            {"id": 0, "name": "sea", "supercategory": "natural"},
            {"id": 1, "name": "oil_spill", "supercategory": "oil_spill"},
            {"id": 2, "name": "look_alike", "supercategory": "no_oil_spill"},
            {"id": 3, "name": "ship", "supercategory": "vessel"},
            {"id": 4, "name": "land", "supercategory": "natural"},
        ],
    }
    # Create the images and annotations
    image_id = 0
    annotation_id = 0
    for folder in os.listdir(input_dir):
        # Skip folder is not subset
        if folder != subset:
            continue
        # Skip the files that are not folders
        if os.path.isdir(os.path.join(input_dir, folder)):
            # Walk over images folder
            for file in os.listdir(os.path.join(input_dir, folder, "images")):
                print(file)
                if file.endswith(".jpg"):
                    image_id += 1
                    # Add the image
                    image = {
                        "id": image_id,
                        "file_name": file,
                        "width": 1250,
                        "height": 650,
                    }
                    coco_dataset["images"].append(image)
                    # Add the annotation
                    # TODO: Implement the categories, segmentations and bbox part using instance masks
                    #  instead of segmentation masks.
                    annotation = {
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": None,
                        "segmentation": [],
                        "area": 0,
                        "bbox": [],
                        "iscrowd": 0,
                    }
                    coco_dataset["annotations"].append(annotation)
                    annotation_id += 1
    # Save the COCO dataset
    print("Saving reformated dataset to: {}".format(output_dir))
    with open(os.path.join(output_dir, "annotations.json".format(subset)), "w") as f:
        json.dump(coco_dataset, f)

    # Copy the images
    output_images_dir = os.path.join(output_dir, "images")
    print("Copying images to: {}".format(output_images_dir))
    # Create the output images directory if it does not exist
    if not os.path.exists(output_images_dir):
        os.makedirs(output_images_dir)
    for folder in os.listdir(input_dir):
        # Skip folder is not subset
        if folder != subset:
            continue
        # Skip the files that are not folders
        if os.path.isdir(os.path.join(input_dir, folder)):
            # Walk over images folder
            input_images_dir = os.path.join(input_dir, folder, "images")
            for file in os.listdir(input_images_dir):
                if file.endswith(".jpg"):
                    os.system(
                        "cp {} {}".format(
                            os.path.join(input_images_dir, file),
                            os.path.join(output_images_dir, file),
                        )
                    )
    print("Done!")


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
