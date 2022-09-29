# Dockerfile for the Docker image that will be used to build the project

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Arguments
ARG NVIDIA_RELEASE=20.09
ARG PYTHON_VERSION_FLAG=py3
ARG PLATFORM=tensorflow
ARG TF_VERSION_FLAG=tf2

# Build an image from NVIDIA NGC (Repository for NVIDIA Optimized Frameworks)
# Release 20.09 is based on CUDA 11.0.3, which requires NVIDIA driver release 450.51
# compatible with NVIDIA GPUs of CEDIA's HPC
FROM nvcr.io/nvidia/${PLATFORM}:${NVIDIA_RELEASE}-${TF_VERSION_FLAG}-${PYTHON_VERSION_FLAG}

# Set maintener
LABEL maintainer="Juan Carlos Cedeño <juancn95@gmail.com>"

# Set project directory
WORKDIR /oil-spill-SAR

# Add PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Copy requirements.txt to the container at work directory
COPY requirements.txt .

# Install dependencies
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN rm requirements.txt

# Install other dependencies such as linters. This is not necessary for the project
RUN pip install black

# Expose Tensorboard Port
EXPOSE 6006

# Expose Jupyter Port
EXPOSE 8888