#!/bin/sh
# Downloading Workflow: Script to download all Sentinel-1 SAR images used in the project.
# This dataset consists of almost 10000 images along Ecuadorian Exclusive Economic Zone, each of ~1GB.

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Read dotenv located in the root of the project
set -a
[ -f .env ] && . .env

# Check if DHUS_USER and DHUS_PASSWORD variable are set
if [ -z "$DHUS_USER" ] || [ -z "$DHUS_PASSWORD" ]; then
    echo "DHUS_USER and DHUS_PASSWORD variables are not set. Please set them in the .env file."
    exit 1
fi

# Check if the sentinel_1 exists under the unprocessed data folder
if [ ! -d "./data/unprocessed/sentinel_1" ]; then
    mkdir -p "./data/unprocessed/sentinel_1"
fi

# Download Sentinel-1 SAR images
sentinelsat --sentinel 1 --producttype GRD --start 20150101 --end 20200101 -g ./data/aoi.geojson --path ./data/unprocessed/sentinel_1 -d
