#!/bin/sh
# Enroot Workflow: Script to create an unprivileged rootfs container (GPU capabilities enabled) from a docker image

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Set arguments
NVIDIA_RELEASE=21.07
PYTHON_VERSION_FLAG=py3
COCO_API_VERSION=v0.6.0
PLATFORM=tensorflow
TF_VERSION_FLAG=tf2
PROJECT=oil-spill-SAR
WORK_DIR="/workspace/${PROJECT}"
SQSH_FILENAME=oil-spill-sar+tf2+py3.sqsh
ROOT_DIR="${HOME}/${PROJECT}"
SQSH_FILE="${ROOT_DIR}/${SQSH_FILENAME}"
ESA_SNAP="esa-snap_sentinel_unix_8_0.sh"
ESA_SNAP_LINK="https://download.esa.int/step/snap/8.0/installers/${ESA_SNAP}"

# Delete any SQSH file locate in the root directory
if test -f "$SQSH_FILE"; then
#   Checks if .sqsh file exists, then delete it
    rm "$SQSH_FILE"
fi
# Build an SQSH image of Tensorflow from NVIDIA NGC (Repository for NVIDIA Optimized Frameworks)
# Release 20.09 is based on CUDA 11.4, which requires NVIDIA driver release 470 or later
# compatible with NVIDIA GPUs of CEDIA's HPC
printf "\nBuilding an SQSH image of Tensorflow from NVIDIA NGC (Repository for NVIDIA Optimized Frameworks)...\n"
enroot import --output "$SQSH_FILE" "docker://nvcr.io#nvidia/${PLATFORM}:${NVIDIA_RELEASE}-${TF_VERSION_FLAG}-${PYTHON_VERSION_FLAG}"
# Create an container rootfs (RF) from SQSH file downloaded
printf "\nCreating an container rootfs (RF) from SQSH file downloaded...\n"
enroot create --force --name $PROJECT "$SQSH_FILE"
# Update and install packages
printf "\nUpdating and installing packages in the container...\n"
enroot start --root --rw $PROJECT sh -c 'apt update -y && apt install gdal-bin libsqlite3-mod-spatialite -y'
# Install Sentinel Application Platform (SNAP) v8
printf "\nInstalling Sentinel Application Platform (SNAP) v8 in the container...\n"
enroot start --rw --mount "$PWD":$WORK_DIR $PROJECT sh -c "wget -O ${ESA_SNAP} ${ESA_SNAP_LINK} && chmod +x ${ESA_SNAP} && ./${ESA_SNAP} -q -varfile ${WORK_DIR}/esa-snap_install_unix_8_0.varfile"
# Install python dependencies
printf "\nInstalling python dependencies in the container...\n"
enroot start --rw --mount "$PWD":$WORK_DIR $PROJECT sh -c "cd ${WORK_DIR} && pip --no-cache-dir install -r requirements.txt"