#!/usr/bin/env bash
# Copyright 2014, Rackspace US, Inc.
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

set -e -o -v

WORK_DIR="/opt/ansible-lxc-rpc"
GIT_REPO="https://github.com/rcbops/ansible-lxc-rpc"
REPO_PACKAGES_PATH="/opt/ansible-lxc-rpc/rpc_deployment/vars/repo_packages/"
OUTPUT_WHEEL_PATH="/var/www/repo/python_packages"
RELEASE=$1

rm -rf /tmp/rpc_wheels*
rm -rf /tmp/pip*
rm -rf "${WORK_DIR}"

git clone "${GIT_REPO}" "${WORK_DIR}"
pushd "${WORK_DIR}"
  git checkout "${RELEASE}"
popd

${WORK_DIR}/scripts/rpc-wheel-builder.py -i "${REPO_PACKAGES_PATH}" \
                                         -o "${OUTPUT_WHEEL_PATH}"/"${RELEASE}"
