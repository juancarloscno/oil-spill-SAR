#!/bin/bash
# Containerization Workflow Script
# This script launch unprivileged sandbox created with GPU capabilities enabled
# Copyright (c) 2022 Juan Carlos Cedeño
# Licensed under the MIT License (see LICENSE for details)
# Written by Juan Carlos Cedeño

# Export environments variable from dotenv
export $(cat ~/oil-spill-SAR/.env | xargs)

# Start the container with read/write mode and execute in interactive mode
enroot start --rw --env TF_FORCE_GPU_ALLOW_GROWTH=$TF_FORCE_GPU_ALLOW_GROWTH \
                  --env CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
                  --env MAPBOX_API_TOKEN=$MAPBOX_API_TOKEN \
                  oil-spill-SAR