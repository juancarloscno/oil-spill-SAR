#!/bin/bash
# Enroot Workflow: Script to run the created enroot container

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Export environments variable from dotenv
export $(cat ~/oil-spill-SAR/.env | xargs)

# Start the container with read/write mode and execute in interactive mode
enroot start --rw --env TF_FORCE_GPU_ALLOW_GROWTH=$TF_FORCE_GPU_ALLOW_GROWTH \
                  --env CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
                  --env MAPBOX_API_TOKEN=$MAPBOX_API_TOKEN \
                  oil-spill-SAR