#!/bin/bash
# Docker Workflow Script
# This script automates the build process of a docker image
# Copyright (c) 2021 Juan Carlos Cedeño
# Licensed under the MIT License (see LICENSE for details)
# Written by Juan Carlos Cedeño

# Build the docker image with tag:latest
docker build . -t oil-spill-sar