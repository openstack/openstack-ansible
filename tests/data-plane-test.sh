#!/bin/bash
# Copyright 2017, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

## Shell Opts ----------------------------------------------------------------
set -e -x

## Vars ----------------------------------------------------------------------

# Log file location
TEST_LOG_FILE="/var/log/data-plane-test.log"

# The test instance name
INSTANCE_NAME="test1"

# Test script socket file location
TEST_SOCKET_FILE="/var/run/data-plane-test.socket"

# Disk access test script
DISK_ACCESS_SCRIPT="/opt/openstack-ansible/tests/disk-access-test.sh"

# Disk access log file
DISK_ACCESS_LOG="~/disk-access-test.log"

# Setup counters
PASS=0
FAIL=0

# SSH/SCP prefixes
CMD_SCP_PREFIX="sshpass -p cubswin:) scp -o StrictHostKeyChecking=no"
CMD_SSH_PREFIX="sshpass -p cubswin:) ssh -o StrictHostKeyChecking=no"

## Functions -----------------------------------------------------------------

# Create a demorc file with auth credentials
# and other state tracking information.
setup_demorc() {
    cp /root/openrc /root/demorc
    sed -i 's/OS_PROJECT_NAME=.*/OS_PROJECT_NAME=demo/' /root/demorc
    sed -i 's/OS_TENANT_NAME=.*/OS_TENANT_NAME=demo/' /root/demorc
    sed -i 's/OS_USERNAME=.*/OS_USERNAME=demo/' /root/demorc
    sed -i 's/OS_PASSWORD=.*/OS_PASSWORD=demo/' /root/demorc
    echo "INSTANCE_NAME=${INSTANCE_NAME}" >> /root/demorc
    echo "TEST_LOG_FILE=${TEST_LOG_FILE}" >> /root/demorc
    echo "TEST_SOCKET_FILE=${TEST_SOCKET_FILE}" >> /root/demorc
}

# Log results
result_log() {
    # We want the output format to be:
    # YYYY-MM-DD HH:MM:SS <result>
    STAMP=$(date -u "+%Y-%m-%d %H:%M:%S")
    echo "${STAMP} ${1}" >> ${TEST_LOG_FILE}
}

# Tests to execute
tests() {
    # A simple end-to-end test to verify that we can login via the floating
    # IP address and can read data from the disk.
    CMD_CONNECT="timeout 1s ${CMD_SSH_PREFIX} cirros@${INSTANCE_PUBLIC_ADDRESS}"
    if ${CMD_CONNECT} cat /etc/issue > /dev/null; then
        result_log PASS
        PASS=$((PASS+1))
    else
        result_log FAIL
        FAIL=$((FAIL+1))
    fi
}

# Steps to execute when finishing
finish() {
    finish_disk_test
    rm -f ${TEST_SOCKET_FILE} > /dev/null
    echo "PASS: ${PASS}" >> ${TEST_LOG_FILE}
    echo "FAIL: ${FAIL}" >> ${TEST_LOG_FILE}
}

# Setup the disk access test
setup_disk_test() {
    # Copy the disk access test script to the instance
    ${CMD_SCP_PREFIX} ${DISK_ACCESS_SCRIPT} cirros@${INSTANCE_PUBLIC_ADDRESS}:~

    # Initiate the disk access test in the instance
    CMD_TO_START="sudo /bin/sh disk-access-test.sh > ${DISK_ACCESS_LOG} &"
    ${CMD_SSH_PREFIX} cirros@${INSTANCE_PUBLIC_ADDRESS} "${CMD_TO_START}"
}

# Finish the disk access test
finish_disk_test() {
    # Remove the socket file to stop the test
    ${CMD_SSH_PREFIX} cirros@${INSTANCE_PUBLIC_ADDRESS} sudo rm -f /var/run/disk-access-test.socket

    # Wait 2s for test to finalise
    sleep 2

    # Fetch the log file with the results
    ${CMD_SCP_PREFIX} cirros@${INSTANCE_PUBLIC_ADDRESS}:${DISK_ACCESS_LOG} /var/log/disk-access-log.log
}

# Setup the trap for the interrupt
trap finish SIGHUP SIGINT SIGTERM

## Main ----------------------------------------------------------------------

# Create the demorc file if it doesn't exist
if [[ ! -f /root/demorc ]]; then
    setup_demorc
fi

# Fetch the environment variables to be used
source /root/demorc

# Create a volume for the test instance to use for the disk access test
if [ -z ${INSTANCE_VOLUME_UUID+x} ]; then
    INSTANCE_VOLUME_UUID=$(openstack volume create --size 1 ${INSTANCE_NAME} --column id --format value)
    echo "INSTANCE_VOLUME_UUID=${INSTANCE_VOLUME_UUID}" >> /root/demorc
fi

# Register the private network UUID
if [ -z ${INSTANCE_NETWORK_UUID+x} ]; then
    INSTANCE_NETWORK_UUID=$(openstack network show private --column id --format value)
    echo "INSTANCE_NETWORK_UUID=${INSTANCE_NETWORK_UUID}" >> /root/demorc
fi

# If a test instance does not exist, create it
if [ -z ${INSTANCE_UUID+x} ]; then
    INSTANCE_UUID=$(openstack server create --flavor tempest1 --image cirros ${INSTANCE_NAME} --nic net-id=${INSTANCE_NETWORK_UUID} --column id --format value)
    echo "INSTANCE_UUID=${INSTANCE_UUID}" >> /root/demorc
fi

# If a floating IP address has not been allocated, do so
if [ -z ${INSTANCE_PUBLIC_ADDRESS+x} ]; then
    INSTANCE_PUBLIC_ADDRESS=$(openstack floating ip create public --column floating_ip_address --format value)
    echo "INSTANCE_PUBLIC_ADDRESS=${INSTANCE_PUBLIC_ADDRESS}" >> /root/demorc
fi

# Wait for the server to be ready
while [[ "$(openstack server show ${INSTANCE_UUID} --column status --format value)" != "ACTIVE" ]]; do
  sleep 4
done

# If the floating IP is not associated with the test instance, associate it
if ! openstack server show ${INSTANCE_UUID} --column addresses --format value | grep -q ${INSTANCE_PUBLIC_ADDRESS}; then
    openstack server add floating ip ${INSTANCE_UUID} ${INSTANCE_PUBLIC_ADDRESS}
fi

# Wait for the volume to be ready
while [[ "$(openstack volume show ${INSTANCE_VOLUME_UUID} --column status --format value)" != "available" ]]; do
  sleep 4
done

# Attach the volume to the test instance
openstack server add volume ${INSTANCE_UUID} ${INSTANCE_VOLUME_UUID}

# Wait for the volume to show as in-use
while [[ "$(openstack volume show ${INSTANCE_VOLUME_UUID} --column status --format value)" != "in-use" ]]; do
  sleep 4
done

# Start the disk access test in the instance
setup_disk_test

# Setup the socket file to allow termination later
echo $$ > ${TEST_SOCKET_FILE}

# Execute the test loop
while [ -f "${TEST_SOCKET_FILE}" ]; do
    tests
    sleep 1
done

# This point will only be reached if the
# socket file is removed
finish
