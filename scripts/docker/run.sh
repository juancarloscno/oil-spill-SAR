#!/bin/bash
# Docker Workflow: Script to run the created docker image

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.


# Run a container in interactive mode and expose default ports
# Port 8888 is for Jupyter Notebook
# Port 8887 is for Jupyter Notebook (use it when port will be busy)
# Port 6006 is for Tensorboard
docker run --rm -it \
  -p 6006:6006 -p 8888:8888 -p 8887:8887 \
  -v $PWD:/workspace/oil-spill-SAR \
  oil-spill-sar