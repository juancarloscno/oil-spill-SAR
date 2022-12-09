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
JPY_REPO="https://github.com/bcdev/jpy.git"
PYTHON_DIR="/usr/bin/python3.8"

# Download the SNAP installer from the ESA website in temporary folder and execute the installation using the varfile
wget -O /tmp/${ESA_SNAP_PKG} ${ESA_SNAP_LINK}
chmod +x /tmp/${ESA_SNAP_PKG} && /tmp/${ESA_SNAP_PKG} -q -varfile $ESA_SNAP_VARFILE_FILEPATH

# Export variables related with JAVA
export JDK_HOME="/usr/lib/jvm/java-1.8.0-openjdk-amd64"
export JAVA_HOME=$JDK_HOME
# Set JAVA_HOME in the SNAP configuration file, permanently. Otherwise, JAVA_HOME will be set each time the container is started
sed -i "s+jdkhome=.*+jdkhome=$JAVA_HOME+g" /opt/snap/etc/snap.conf

# Test if snappy folder exists under $SNAP_DIR, if not then created it
if [ ! -d "${SNAP_DIR}/snappy" ]; then
    mkdir -p ${SNAP_DIR}/snappy
fi
# Move to the snappy folder
cd $SNAP_DIR/snappy
# Download the JPY repository from the GitHub and build its wheels
git clone $JPY_REPO
cd jpy
python setup.py bdist_wheel
# Move the JPY wheel to the snappy folder
JPY_WHEEL=$(find dist -name "*.whl")
JPY_WHEEL_FILENAME=$(basename "$JPY_WHEEL")
cp "$JPY_WHEEL" ${SNAP_DIR}/snappy/"${JPY_WHEEL_FILENAME}"

# Run snappy-conf to configure snappy for Python 3.8
$SNAP_DIR/bin/snappy-conf $PYTHON_DIR $SNAP_DIR

# Copy snappy under dist-packages
cd $SNAP_DIR/snappy && python3 setup.py install