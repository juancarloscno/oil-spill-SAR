from src.data.dataset.factory import Dataset
from src.utils.definitions import UNPROCESSED_DATA_DIR
from src.utils.miscellaneous import download_url, extract_all_files
from src.features.connected_components import (
    get_bitmask,
    get_connected_component_labels,
)
from src.coco.utils import encode_mask, bbox_from_encoded_mask, area_from_encoded_mask
from dotenv import find_dotenv, load_dotenv
from pycocotools.coco import COCO
from pycocotools import mask as mask_utils
import os
import json
import cv2
import numpy as np


class OilSpillDetectionDataset(Dataset):
    LABELS_VALUES = {
        "sea": 0,
        "oil_spill": 1,
        "look_alike": 2,
        "ship": 3,
        "land": 4,
    }

    NAME_VALUES = {
        0: "sea",
        1: "oil_spill",
        2: "look_alike",
        3: "ship",
        4: "land",
    }

    def load_oil_spills(self, dataset_dir, subset, class_names=None):
        # class name used to labeling [source, class_id, class_name]
        # Assertion of subset
        assert subset in ["train", "test"]
        # Read COCO annotation
        dataset = COCO(os.path.join(dataset_dir, subset, "annotations.json"))
        # Load all classes or a subset
        if not class_names:
            class_ids = sorted(dataset.getCatIds())
        else:
            class_ids = [self.LABELS_VALUES[class_name] for class_name in class_names]
        # Create the images directory
        images_dir = os.path.join(dataset_dir, subset, "images")
        # Get images ids
        if class_names:
            image_ids = []
            for id in class_ids:
                image_ids.extend(dataset.getImgIds(catIds=[id]))
                # Remove duplicates
                image_ids = list(set(image_ids))
        else:
            image_ids = list(dataset.imgs.keys())

        # Add classes
        for i in class_ids:
            self.add_class("mklab", i, dataset.loadCats(i)[0]["name"])

        # Add images
        for i in image_ids:
            self.add_image(
                "mklab",
                image_id=i,
                path=os.path.join(images_dir, dataset.imgs[i]["file_name"]),
                width=dataset.imgs[i]["width"],
                height=dataset.imgs[i]["height"],
                annotations=dataset.loadAnns(
                    dataset.getAnnIds(imgIds=[i], catIds=class_ids, iscrowd=None)
                ),
            )

    def load_mask(self, image_id):
        """Load instance masks for the given image id.

        Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: A 1-D array of class IDs of the instance masks.
        """

        # Get dict with the image info
        image_info = self.image_info[image_id]
        # Return label path of the image mask
        instance_masks = []
        class_ids = []
        annotations = self.image_info[image_id]["annotations"]

        for annotation in annotations:
            class_id = self.map_source_class_id(
                "mklab.{}".format(annotation["category_id"])
            )
            if class_id:
                mask = self.annToMask(
                    annotation, image_info["height"], image_info["width"]
                )

                if mask.max() < 1:
                    continue

                if annotation["iscrowd"]:
                    class_id *= -1

                    if (
                            mask.shape[0] != image_info["height"]
                            or mask.shape[1] != image_info["width"]
                    ):
                        mask = np.ones(
                            [image_info["height"], image_info["width"]], dtype=bool
                        )
                instance_masks.append(mask)
                class_ids.append(class_id)

        if class_ids:
            masks = np.stack(instance_masks, axis=2).astype(np.bool)
            class_ids = np.array(class_ids, dtype=np.int32)

        return masks, class_ids

    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "mklab":
            return info["id"]
        else:
            super(self.__class__, self).image_reference(image_id)

    def annToRLE(self, ann, height, width):
        """Convert annotation which can be polygons, uncompressed RLE to RLE.

        Returns:
            A binary mask (numpy 2D array)
        """
        segm = ann["segmentation"]
        if isinstance(segm, list):
            # polygon -- a single object might consist of multiple parts
            # we merge all parts into one mask rle code
            rles = mask_utils.frPyObjects(segm, height, width)
            rle = mask_utils.merge(rles)
        elif isinstance(segm["counts"], list):
            # uncompressed RLE
            rle = mask_utils.frPyObjects(segm, height, width)
        else:
            # rle
            rle = ann["segmentation"]
        return rle

    def annToMask(self, ann, height, width):
        """
        Convert annotation which can be polygons, uncompressed RLE, or RLE to binary mask.
        :return: binary mask (numpy 2D array)
        """
        rle = self.annToRLE(ann, height, width)
        m = mask_utils.decode(rle)
        return m


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
