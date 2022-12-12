#!/bin/bash
# SNAP Workflow: Script to install ESA SNAP v8 in the container

# Copyright (c) 2022 Juan Carlos Cedeño Noblecilla

# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# Written by Juan Carlos Cedeño Noblecilla.

# Arguments
PROJECT="oil-spill-SAR"
WORK_DIR="/workspace/${PROJECT}"
ESA_SNAP_VARFILE="esa-snap_install_unix_8_0.varfile"
ESA_SNAP_VARFILE_FILEPATH="${WORK_DIR}/${ESA_SNAP_VARFILE}"
ESA_SNAP_PKG='esa-snap_sentinel_unix_8_0.sh'
ESA_SNAP_LINK="https://download.esa.int/step/snap/8.0/installers/${ESA_SNAP_PKG}"
SNAP_DIR="/opt/snap"
SNAPPY_DIR="${SNAP_DIR}/snappy"
JPY_DIR="${SNAP_DIR}/jpy"
#JPY_REPO="https://github.com/bcdev/jpy.git"
JPY_REPO="https://github.com/jpy-consortium/jpy.git"
# Only v0.9.0 is valid, other versions crashes the snappy installation
JPY_VERSION="0.9.0"
PYTHON_DIR="/usr/bin/python"

# Download the SNAP installer from the ESA website in temporary folder and execute the installation using the varfile
if [ ! -f "/tmp/${ESA_SNAP_PKG}" ]; then
	echo -e "\nGetting SNAP v.8.0 installer from ESA website...\n"
	wget -O /tmp/${ESA_SNAP_PKG} ${ESA_SNAP_LINK}
	chmod +x /tmp/${ESA_SNAP_PKG} && /tmp/${ESA_SNAP_PKG} -q -varfile $ESA_SNAP_VARFILE_FILEPATH
fi

# Export variables related with JAVA
echo -e "\nExporting JAVA environment variables\n"
export JDK_HOME="/usr/lib/jvm/java-1.8.0-openjdk-amd64"
export JAVA_HOME="${JDK_HOME}"
export LD_LIBRARY_PATH="${JDK_HOME}/jre/lib/server:${LD_LIBRARY_PATH}"
# Set JAVA_HOME in the SNAP configuration file, permanently. Otherwise, JAVA_HOME will be set each time the container is started
sed -i "s+jdkhome=.*+jdkhome=$JAVA_HOME+g" /opt/snap/etc/snap.conf

# Test if snappy folder exists under $SNAP_DIR, if not then created it
if [ ! -d $SNAPPY_DIR ]; then
    mkdir -p $SNAPPY_DIR
fi

# Download the JPY repository from the GitHub and build its wheels
cd $SNAP_DIR
git clone -b $JPY_VERSION $JPY_REPO
cd jpy
pip install --upgrade pip wheel
python setup.py build maven bdist_wheel

# Find wheel of JPY
JPY_WHEEL=$(find dist -name "*.whl")
JPY_WHEEL_FILENAME=$(basename "$JPY_WHEEL")
# Move JPY wheel to snappy folder
echo -e "\nCopy $JPY_WHEEL to $SNAPPY_DIR/$JPY_WHEEL_FILENAME\n"
cp "$JPY_WHEEL" "${SNAPPY_DIR}/${JPY_WHEEL_FILENAME}"

# Launch snappy-conf to configure snappy for Python 3.8
echo -e "\nInstalling The Sentinel Application Platform (SNAP)...\n"
$SNAP_DIR/bin/snappy-conf $PYTHON_DIR $SNAP_DIR
echo -e "\nSNAP has been installed successfully!\n"

# Updating SNAP
echo -e "\nUpdating SNAP modules..."
$SNAP_DIR/bin/snap --nosplash --nogui --modules --update-all
echo -e "\nSNAP modules has been updated sucessfully!\n"

# Install Snappy and JPY locally
cd $SNAPPY_DIR/snappy && python setup.py install
cd $JPY_DIR/dist && pip install $JPY_WHEEL_FILENAME

# Install Snapista
pip install lxml
pip install --use-pep517 git+https://github.com/snap-contrib/snapista.git

# Add GPT to the PATH, permanently, because Snapista read 'GPT' trhough $PATH variable
echo -e '\nPATH="/opt/snap/bin":$PATH' >> $HOME/.profile
echo -e "\nJDK_HOME="$JDK_HOME"" >> $HOME/.profile
echo -e "\nJAVA_HOME="$JAVA_HOME"" >> $HOME/.profile
