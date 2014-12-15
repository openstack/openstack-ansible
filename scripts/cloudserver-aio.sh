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
set -e -u -v -x

REPO_URL=${REPO_URL:-"https://github.com/stackforge/os-ansible-deployment.git"}
REPO_BRANCH=${REPO_BRANCH:-"master"}
WORKING_FOLDER=${WORKING_FOLDER:-"/opt/stackforge/os-ansible-deployment"}

# install git so that we can fetch the repo
apt-get update && apt-get install -y git

# fetch the repo
git clone -b ${REPO_BRANCH} ${REPO_URL} ${WORKING_FOLDER}/

# run the same aio build script that is used in the OpenStack CI pipeline
cd ${WORKING_FOLDER}
./scripts/os-ansible-aio-check.sh
