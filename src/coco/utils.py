import numpy as np
import six
from pycocotools import mask as mask_utils


def encode_mask(mask, dtype=np.uint8):
    """Encodes a binary mask using the RLE format.

    Args:
    mask (np.ndarray): A binary numpy array of shape [height, width]
    dtype (type): The data type of the encoded mask. Default: np.uint8

    Returns:
        A dictionary that can be stored in COCO format.
    """
    if mask.dtype != dtype:
        mask = mask.astype(dtype)
    encoded_mask = mask_utils.encode(np.asfortranarray(mask))
    return encoded_mask
    rle = mask_utils.encode(np.asfortranarray(mask, dtype=dtype))
    rle["counts"] = six.ensure_str(rle["counts"])
    return rle


def area_from_encoded_mask(encoded_mask):
    """Computes area of an encoded mask.

    Args:
        encoded_mask (dict): A dictionary that can be stored in COCO format.

    Returns:
        The area of the mask.
    """
    return mask_utils.area(encoded_mask)


def bbox_from_encoded_mask(encoded_mask):
    """Computes bounding box from an encoded mask.

    Args:
        encoded_mask (dict): A dictionary that can be stored in COCO format.

    Returns:
        A list of bounding box coordinates in the format [x_min, y_min, width, height].
    """
    return mask_utils.toBbox(encoded_mask)
