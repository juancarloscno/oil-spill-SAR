from src.utils.definitions import UNPROCESSED_DATA_DIR
from src.utils.miscellaneous import download_url, extract_all_files
from src.features.connected_components import (
    get_bitmask,
    get_connected_component_labels,
)
from src.coco.utils import encode_mask, bbox_from_encoded_mask, area_from_encoded_mask
from dotenv import find_dotenv, load_dotenv
import os
import json
import cv2
import numpy as np


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
                    ## Annotations section
                    # Read the segmentation mask
                    filepath = os.path.join(
                        input_dir, folder, "labels_1D", file.replace(".jpg", ".png")
                    )
                    mask = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
                    n_classes = np.max(mask) + 1
                    if n_classes == 1:
                        # The image is empty
                        continue
                    # Create the segmentation
                    for c in range(n_classes):
                        # Skip the background class
                        if c == 0:
                            continue
                        # Get a bitmask of the class-of-interest from segmentation mask
                        bitmask = get_bitmask(mask, c)
                        # Get connected components
                        num_labels, labels = get_connected_component_labels(bitmask)
                        if num_labels == 1:
                            # If there is only one connected component, num_labels is equal to 2.
                            # But, when there is not a connected component, num_labels is equal to 1, so
                            # is assumed that the segmentation mask is an 2d-array filled with zeros.
                            # Then, we skip it.
                            continue
                        for k in range(1, num_labels):
                            # The range starts from 1 because k=0 is the background.
                            # Get the connected component
                            instance_mask = get_bitmask(labels, k)
                            # Get the bounding box
                            encoded_mask = encode_mask(instance_mask)
                            # Create the annotation
                            annotation = {
                                "id": annotation_id,
                                "image_id": image_id,
                                "category_id": c,
                                "segmentation": encoded_mask,
                                "area": int(
                                    area_from_encoded_mask(encoded_mask)
                                ),  # int() is necessary
                                "bbox": bbox_from_encoded_mask(encoded_mask)
                                .astype(int)
                                .tolist(),
                                # int() is necessary
                                "iscrowd": 0,
                            }
                            coco_dataset["annotations"].append(annotation)
                            annotation_id += 1
    # Save the COCO dataset
    print("Saving reformated dataset to: {}".format(output_dir))
    with open(os.path.join(output_dir, "annotations.json"), "w") as f:
        json.dump(coco_dataset, f, indent=4, sort_keys=True)

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


if __name__ == "__main__":
    download_mklab_dataset()
