#!/bin/bash
# Docker Workflow Script
# This script runs a clean container from the image created
# Copyright (c) 2021 Juan Carlos Cedeño
# Licensed under the MIT License (see LICENSE for details)
# Written by Juan Carlos Cedeño

# Run a container in interactive mode and expose default ports
# Port 8888 is for Jupyter Notebook
# Port 8887 is for Jupyter Notebook (use it when port will be busy)
# Port 6006 is for Tensorboard
docker run --rm -it \
  -p 6006:6006 -p 8888:8888 -p 8887:8887 \
  -v $PWD:/workspace/oil-spill-SAR \
  oil-spill-sar