#!/bin/bash
# Enroot Workflow: Script to create an unprivileged rootfs container (GPU capabilities enabled) from a docker image

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Set environment variables from dotenv
export $(cat ~/oil-spill-SAR/.env | xargs)
# Set arguments
NVIDIA_RELEASE=21.07
PYTHON_VERSION_FLAG=py3
COCO_API_VERSION=v0.6.0
PLATFORM=tensorflow
TF_VERSION_FLAG=tf2
PROJECT=oil-spill-SAR
SQSH_FILENAME=oil-spill-sar+tf2+py3.sqsh
ROOT_DIR="${HOME}/${PROJECT}"
SQSH_FILE="${ROOT_DIR}/${SQSH_FILENAME}"


# Create a flag using getopts with the following options:
# -d: Create a development container. 
# -p: Create a production container
# -h: Show help
DEV=0
PROD=0
while getopts "d:ph" opt; do
  case $opt in
    d) DEV=$OPTARG
    # Test if vscode or projector has been choosen
    if [[ $DEV != "vscode" && $DEV != "projector" ]]; then
      echo "Invalid option: $DEV. Valid options are: vscode or projector"
      exit 1
    fi
    ;;
    p) PROD=1
    ;;
    h) HELP_FLAG=1
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

# If the help flag is set, show the help message
if [ $HELP_FLAG ]; then
  echo "Usage: build.sh [OPTION]..."
  echo "Create an unprivileged rootfs container (GPU capabilities enabled) from a custom docker image"
  echo ""
  echo "Options:"
  echo "-d: Create a development container. This flag has two options: <vscode> OR <projector>"
  echo "-p: Create a production container"
  echo "-h: Show help"
  exit 0
fi

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
enroot start --rw --mount "${HOME}"/oil-spill-SAR:"${HOME}"/oil-spill-SAR \ 
    sh -c cd "${HOME}"/oil-spill-SAR & \
    python3 -m pip install -U pip & \ 
    pip --no-cache-dir install -r "${HOME}"/oil-spill-SAR/requirements.txt