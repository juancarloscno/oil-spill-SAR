#!/bin/bash
# Enroot Workflow: Script to run the created enroot container

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Arguments
PROJECT="oil-spill-SAR"
WORK_DIR="/workspace/${PROJECT}"

# Start the container with read/write mode and execute in interactive mode
enroot start --rw --mount "$PWD":$WORK_DIR $PROJECT sh -c "cd ${WORK_DIR} && bash"