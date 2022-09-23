"""
Definitions
This module loads folder structure and other definitions as global variables.d

Copyright (c) 2020 Juan Carlos Cedeño.
Licensed under the MIT License (see LICENSE for details)
Written by Juan Carlos Cedeño.
"""

import os

# First level dirs
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ROOT_DIR = os.path.abspath(os.path.join(SRC_DIR, os.pardir))
DATA_DIR = os.path.join(ROOT_DIR, "data")
