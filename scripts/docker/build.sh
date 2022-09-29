#!/bin/bash
# Docker Workflow: Script to automate the build process of a docker image

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Build the docker image with tag:latest
docker build . -t oil-spill-sar