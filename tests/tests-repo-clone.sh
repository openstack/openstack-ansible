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

# PURPOSE:
# This script clones the openstack-ansible-tests repository to the
# tests/common folder in order to be able to re-use test components
# for role testing.

# WARNING:
# This file is maintained in the openstack-ansible-tests repository:
# https://git.openstack.org/cgit/openstack/openstack-ansible-tests
# If you need to change this script, then propose the change there.
# Once it merges, the change will be replicated to the other repositories.

## Shell Opts ----------------------------------------------------------------

set -e

## Vars ----------------------------------------------------------------------

export TESTING_HOME=${TESTING_HOME:-$HOME}
export WORKING_DIR=${WORKING_DIR:-$(pwd)}
export CLONE_UPGRADE_TESTS=${CLONE_UPGRADE_TESTS:-no}
export ZUUL_TESTS_CLONE_LOCATION="/home/zuul/src/opendev.org/openstack/openstack-ansible-tests"

## Functions -----------------------------------------------------------------

function create_tests_clonemap {

# Prepare the clonemap for zuul-cloner to use
cat > ${TESTING_HOME}/tests-clonemap.yaml << EOF
clonemap:
  - name: openstack/openstack-ansible-tests
    dest: ${WORKING_DIR}/tests/common
EOF

}

## Main ----------------------------------------------------------------------

# If zuul-cloner is present, use it so that we
# also include any dependent patches from the
# tests repo noted in the commit message.
# We only want to use zuul-cloner if we detect
# zuul v2 running, so we check for the presence
# of the ZUUL_REF environment variable.
# ref: http://git.openstack.org/cgit/openstack-infra/zuul/tree/zuul/ansible/filter/zuul_filters.py?h=feature/zuulv3#n17
if [[ -x /usr/zuul-env/bin/zuul-cloner ]] && [[ "${ZUUL_REF:-none}" != "none" ]]; then

    # Prepare the clonemap for zuul-cloner to use
    create_tests_clonemap

    # Execute the clone
    /usr/zuul-env/bin/zuul-cloner \
        --cache-dir /opt/git \
        --map ${TESTING_HOME}/tests-clonemap.yaml \
        https://opendev.org \
        openstack/openstack-ansible-tests

    # Clean up the clonemap.
    rm -f ${TESTING_HOME}/tests-clonemap.yaml

# Alternatively, use a simple git-clone. We do
# not re-clone if the directory exists already
# to prevent overwriting any local changes which
# may have been made.
elif [[ ! -d tests/common ]]; then

    # The tests repo doesn't need a clone, we can just
    # symlink it. As zuul v3 clones into a folder called
    # 'workspace' we have to use one of its environment
    # variables to determine the project name.
    if [[ "${ZUUL_SHORT_PROJECT_NAME:-none}" == "openstack-ansible-tests" ]] ||\
       [[ "$(basename ${WORKING_DIR})" == "openstack-ansible-tests" ]]; then
        ln -s ${WORKING_DIR} ${WORKING_DIR}/tests/common

    # In zuul v3 any dependent repository is placed into
    # /home/zuul/src/git.openstack.org, so we check to see
    # if there is a tests checkout there already. If so, we
    # symlink that and use it.
    elif [[ -d "${ZUUL_TESTS_CLONE_LOCATION}" ]]; then
        ln -s "${ZUUL_TESTS_CLONE_LOCATION}" ${WORKING_DIR}/tests/common

    # Otherwise we're clearly not in zuul or using a previously setup
    # repo in some way, so just clone it from upstream.
    else
        git clone -b stable/queens \
            https://opendev.org/openstack/openstack-ansible-tests \
            ${WORKING_DIR}/tests/common
    fi
fi

# If this test set includes an upgrade test, the
# previous stable release tests repo must also be
# cloned.
# Note:
# Dependent patches to the previous stable release
# tests repo are not supported.
if [[ "${CLONE_UPGRADE_TESTS}" == "yes" ]]; then
    if [[ ! -d "${WORKING_DIR}/tests/common/previous" ]]; then
        git clone -b stable/pike \
            https://opendev.org/openstack/openstack-ansible-tests \
            ${WORKING_DIR}/tests/common/previous
  fi
fi
