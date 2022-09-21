#!/bin/bash
# Installer Workflow Script
# This script create an unprivileged rootfs container with SNAP Toolbox, GTP and Snapista (Thin layer of GTP for Python)
# for preprocess Sentinel-1 images downloaded from Copernicus Open Access Hub
# Copyright (c) 2022 Juan Carlos Cedeño
# Licensed under the MIT License (see LICENSE for details)
# Written by Juan Carlos Cedeño

# Arguments
PROJECT=oil-spill-SAR
SQSH_NAME="${PROJECT}-pre"
SQSH_FILENAME="${SQSH_NAME}.sqsh"
ROOT_DIR="${HOME}/${PROJECT}"
SQSH_FILE="${ROOT_DIR}/${SQSH_FILENAME}"
# Delete any SQSH file locate in the root directory
if test -f "$SQSH_FILE"; then
#   Checks if .sqsh file exists, then delete it
    rm "$SQSH_FILE"
fi
# Build an SQSH image of SNAP Toolbox from Github Registry
enroot import --output "$SQSH_FILE" docker://ghcr.io#snap-contrib/docker-snap/snap:latest
# Create an container rootfs (RF) from SQSH file downloaded
enroot create --force --name $SQSH_NAME "$SQSH_FILE"
# Install Snapista library for Python
enroot start --root --rw $SQSH_NAME sh -c 'mamba install -y -n env_snap snapista typer'