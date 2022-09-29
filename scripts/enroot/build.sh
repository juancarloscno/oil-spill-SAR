#!/bin/bash
# Enroot Workflow: Script to create an unprivileged rootfs container (GPU capabilities enabled) from a docker image

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Set environment variables from dotenv
export $(cat ~/oil-spill-SAR/.env | xargs)
# Set arguments
NVIDIA_RELEASE=20.09
PYTHON_VERSION_FLAG=py3
PLATFORM=tensorflow
TF_VERSION_FLAG=tf2
PROJECT=oil-spill-SAR
SQSH_FILENAME=oil-spill-sar+tf2+py3.sqsh
ROOT_DIR="${HOME}/${PROJECT}"
SQSH_FILE="${ROOT_DIR}/${SQSH_FILENAME}"
# Delete any SQSH file locate in the root directory
if test -f "$SQSH_FILE"; then
#   Checks if .sqsh file exists, then delete it
    rm "$SQSH_FILE"
fi
# Build an SQSH image of Tensorflow from NVIDIA NGC (Repository for NVIDIA Optimized Frameworks)
# Release 20.09 is based on CUDA 11.0.3, NVIDIA driver release 450.51
# compatible with NVIDIA GPUs of CEDIA's HPC
enroot import --output "$SQSH_FILE" docker://nvcr.io#nvidia/${PLATFORM}:${NVIDIA_RELEASE}-${TF_VERSION_FLAG}-${PYTHON_VERSION_FLAG}
# Create an container rootfs (RF) from SQSH file downloaded
enroot create --force --name $PROJECT "$SQSH_FILE"
# Install python dependencies
enroot start --rw $PROJECT pip --no-cache-dir install opencv-python-headless scikit-image albumentations cupy-cuda110 numba rasterio sentinelsat typer tqdm tabulate python-dotenv geopandas
