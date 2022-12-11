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
JPY_REPO="https://github.com/bcdev/jpy.git"
PYTHON_DIR="/usr/bin/python"

# Download the SNAP installer from the ESA website in temporary folder and execute the installation using the varfile
wget -O /tmp/${ESA_SNAP_PKG} ${ESA_SNAP_LINK}
chmod +x /tmp/${ESA_SNAP_PKG} && /tmp/${ESA_SNAP_PKG} -q -varfile $ESA_SNAP_VARFILE_FILEPATH

# Export variables related with JAVA
export JDK_HOME="/usr/lib/jvm/java-1.8.0-openjdk-amd64"
export JAVA_HOME=$JDK_HOME
# Set JAVA_HOME in the SNAP configuration file, permanently. Otherwise, JAVA_HOME will be set each time the container is started
sed -i "s+jdkhome=.*+jdkhome=$JAVA_HOME+g" /opt/snap/etc/snap.conf

# Test if snappy folder exists under $SNAP_DIR, if not then created it
if [ ! -d $SNAPPY_DIR ]; then
    mkdir -p $SNAPPY_DIR
fi

# Move to the snappy folder
cd $SNAPPY_DIR

# Download the JPY repository from the GitHub and build its wheels
git clone $JPY_REPO
cd jpy
python setup.py bdist_wheel

# Find wheel of JPY
JPY_WHEEL=$(find dist -name "*.whl")
JPY_WHEEL_FILENAME=$(basename "$JPY_WHEEL")
# Move JPY wheel to snappy folder
cp "$JPY_WHEEL" "${SNAPPY_DIR}/${JPY_WHEEL_FILENAME}"
# Remove JPY folder
rm -rf "${SNAPPY_DIR}/jpy"

# Install Snapista library
pip install --use-pep517 git+https://github.com/snap-contrib/snapista.git
pip install lxml

# Launch snappy-conf to configure snappy for Python 3.8
$SNAP_DIR/bin/snappy-conf $PYTHON_DIR $SNAP_DIR

# Install Snappy locally
cd $SNAPPY_DIR && python setup.py install

# Add GPT to the PATH, permanently, because Snapista read 'GPT' trhough $PATH variable
echo -e '\nPATH="/opt/snap/bin":$PATH' >> $HOME/.profile