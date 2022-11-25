"""
Augmentation
Python functions to extract connected components from segmentation masks.

Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

This software is released under the MIT License.
https://opensource.org/licenses/MIT
Written by Juan Carlos Cedeño Noblecilla.
"""

import albumentations as A
import cv2


class Augmentation:
    def __init__(self):
        self.augmenters = []
        self.mask_shape = None
        self.image_shape = None

    def __call__(self, image, mask):
        self.mask_shape = mask.shape  # [height, width]
        self.image_shape = image.shape  # [height, width, 3]
        return self._transform(image, mask)

    def _transform(self, image, mask):
        transformation = A.Compose(transforms=self.augmenters)
        transformed = transformation(image=image, mask=mask)
        # Reshape the image for consistency
        image_transformed = transformed["image"].reshape(self.image_shape)
        # This output mask have an extra dimension (h, w, 1), then, is needed to reshape the mask to the original shape
        # before output it.
        mask_transformed = transformed["mask"].reshape(self.mask_shape)
        return image_transformed, mask_transformed

    @staticmethod
    def random_jitter(height=650, width=1250, height_max=663, width_max=1275, p=0.7):
        """Resize up the input and crops a randomly part of it using its original size."""
        aug = A.Compose(
            [
                A.Resize(
                    height=height_max,
                    width=width_max,
                    interpolation=cv2.INTER_AREA,
                    p=1,
                ),
                A.RandomCrop(height=height, width=width, p=1),
            ],
            p=p,
        )
        return aug

    @staticmethod
    def horizontal_flip(p=0.5):
        """Flip the input horizontally around the y-axis."""
        aug = A.HorizontalFlip(p=p)
        return aug

    @staticmethod
    def vertical_flip(p=0.25):
        """Flip the input vertically around the x-axis."""
        aug = A.VerticalFlip(p=p)
        return aug

    @staticmethod
    def rotation(limit_min=-45, limit_max=45, p=0.5):
        """Rotate the input by an angle selected randomly from the uniform distribution."""
        aug = A.Rotate(limit=(limit_min, limit_max), p=p)
        return aug

    def add(self, x):
        self.augmenters.extend([x])
