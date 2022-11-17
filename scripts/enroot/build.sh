#!/bin/sh
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
# Variables related with Fleet IDE
INSTALL_LOCATION=/usr/local/bin/fleet
INSTALL_URL="https://download.jetbrains.com/product?code=FLL&release.type=preview&release.type=eap&platform=linux_x64"


# Create a flag using getopts with the following options:
# -d: Create a development container. 
# -h: Show help
DEV=0
PROD=0
while getopts "d:ph" opt; do
  case $opt in
    d) DEV_FLAG=1
    DEV=$OPTARG
    # Test if vscode or fleet has been choosen
    if [ $DEV != "vscode" ] && [ $DEV != "fleet" ]; then
      echo "Invalid option: $DEV. Valid options are: vscode or fleet"
      exit 1
    fi
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
  echo "Build an unprivileged rootfs container (GPU capabilities enabled) from a custom docker image"
  echo ""
  echo "Options:"
  echo "-d: Build container in development mode. This flag has two options: <vscode> OR <fleet>"
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
enroot start --rw --mount "$HOME"/oil-spill-SAR:"$HOME"/oil-spill-SAR \
    sh -c cd "$HOME"/oil-spill-SAR & \
    python -m pip install -U pip & \
    pip --no-cache-dir install black & \
    pip --no-cache-dir install -r "$HOME"/oil-spill-SAR/requirements.txt

if [ $DEV_FLAG ]; then
    # Check if $DEV is vscode
    if [ $DEV == "vscode" ]; then
        # Then, install VSCode Server
        echo "Installing VSCode Server by Microsoft..."
        enroot start --rw "$PROJECT" \
        wget -O- https://aka.ms/install-vscode-server/setup.sh | sh
    else
        # Otherwise, install Fleet by JetBrains
        echo "Installing Fleet by JetBrains..."
        enroot start --rw "$PROJECT" \
        curl -sSL "$INSTALL_URL" -o "$INSTALL_LOCATION"
        enroot start --rw --root "$PROJECT" chmod +x "$INSTALL_LOCATION"
    fi
fi
echo "The container has been built successfully!"
