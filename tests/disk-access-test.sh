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
set -e

## Vars ----------------------------------------------------------------------

# Test script socket file location
TEST_SOCKET_FILE="/var/run/disk-access-test.socket"

# The location to write to
TEST_DATA_FILE="/mnt/test"

# Setup counters
PASS=0
FAIL=0

## Functions -----------------------------------------------------------------

# Tests to execute
tests() {
    # We want the output format to be:
    # YYYY-MM-DD HH:MM:SS <result>
    echo -n "$(date -u '+%Y-%m-%d %H:%M:%S') "
    # A simple disk write test to validate whether
    # we are able to write to disk.
    CMD_WRITE="timeout 1s dd bs=1M count=50 if=/dev/zero of=${TEST_DATA_FILE} conv=fdatasync"
    if ${CMD_WRITE}; then
        echo "PASS"
        PASS=$((PASS+1))
    else
        echo "FAIL"
        FAIL=$((FAIL+1))
    fi
}

# Steps to execute when finishing
finish() {
    rm -f ${TEST_SOCKET_FILE} > /dev/null
    echo "PASS: ${PASS}"
    echo "FAIL: ${FAIL}"
}

# Setup the trap for the interrupt
trap finish SIGHUP SIGINT SIGTERM

## Main ----------------------------------------------------------------------

# Partition the volume
echo ';' | sfdisk --quiet /dev/vdb > /dev/null

# Format the volume
mkfs /dev/vdb1 > /dev/null

# Mount the volume
mount /dev/vdb1 /mnt

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
