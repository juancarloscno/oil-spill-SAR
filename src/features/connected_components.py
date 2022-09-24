"""
Labeling Components
Functions to extract connected components form segmentation masks.

Copyright (c) 2020 Juan Carlos Cedeño.
Licensed under the MIT License (see LICENSE for details)
Written by Juan Carlos Cedeño.
"""
import cv2
import numpy as np


def get_bitmask(mask, label_class, dtype=np.uint8):
    """Extract a binary image from a segmentation mask.

    Args:
        mask (np.array): Segmentation mask.
        label_class (int): Class to extract.
        dtype: Data type of the output image. Default is uint8.

    Returns:
        bitmask (np.array): Binary image.
    """
    mask = np.where(mask == label_class, 1, 0).astype(dtype)
    return mask


def get_connected_component_labels(bitmask, connectivity=8):
    """Extract connected components from a binary image.

    Args:
        bitmask (np.array): Binary image.
        connectivity (int): Connectivity value. See OpenCV documentation.

    Returns:
        num_labels (list[np.array]): Connected components.
        labels (list[np.array]): Label images.
    """
    supported_connectivity = [4, 8]
    if connectivity not in supported_connectivity:
        raise ValueError(
            "Connectivity must be one of the following: {}".format(
                supported_connectivity
            )
        )
    num_labels, labels = cv2.connectedComponents(image=bitmask, connectivity=connectivity)
    return num_labels, labels
