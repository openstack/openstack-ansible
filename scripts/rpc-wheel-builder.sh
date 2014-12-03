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

# Notes:
# To use this script you MUST move it to some path that will be called.
# I recommend that the script be stored and executed from 
# "/opt/rpc-wheel-builder.sh". This script is a wrapper script that relies
#  on the "rpc-wheel-builder.py" and is execute from
# "/opt/rpc-wheel-builder.py".

# Overrides:
# This script has several things that can be overriden via environment 
# variables.
#     Git repository that the rcbops ansible lxc source code will be cloned from. 
#     This repo should be a repo that is available via HTTP.
#     GIT_REPO=""

#     The URI for the github api. This is ONLY used when the $RELEASES variable
#     is an empty string. Which causes the script to go discover the available
#     releases.
#     GITHUB_API_ENDPOINT=""

#     Local directory to store the source code while interacting with it.
#     WORK_DIR=""

#     Local directory to store the built wheels.
#     OUTPUT_WHEEL_PATH=""

#     Local directory to store known git repos.
#     OUTPUT_GIT_PATH=""

#     Space seperated list of all releases to build for. If unset the releases
#     will be discovered.
#     RELEASES=""

#     Space seperated list of all releases to exclude from building. This is
#     ONLY used when the $RELEASES variable is an empty string.
#     EXCLUDE_RELEASES=""

set -e -o -v

# Ensure there is a base path loaded
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Defined variables
GIT_REPO="${GIT_REPO:-https://github.com/stackforge/os-ansible-deployment}"
GITHUB_API_ENDPOINT="${GITHUB_API_ENDPOINT:-https://api.github.com/repos/stackforge/os-ansible-deployment}"

WORK_DIR="${WORK_DIR:-/opt/ansible-lxc-rpc}"
REPO_PACKAGES_PATH="${WORK_DIR}/rpc_deployment/vars/repo_packages/"

OUTPUT_WHEEL_PATH="${OUTPUT_WHEEL_PATH:-/var/www/repo/python_packages}"
OUTPUT_GIT_PATH="${OUTPUT_GIT_PATH:-/var/www/repo/rpcgit}"

# Default is an empty string which causes the script to go discover the available
# branches from the github API.
RELEASES=${RELEASES:-""}

EXCLUDE_RELEASES="${EXCLUDE_RELEASES:-v9.0.0 gh-pages revert}"

if [[ ! "${RELEASES}" ]];then
# From the GITHUB API pull a list of all branches/tags
RELEASES=$(
$(which python) <<EOF
import requests

# Create an array of excluded items
EXCLUDE = "${EXCLUDE_RELEASES}".split()

def return_releases(url):
    """Return a list of releases found in the github api.

    :param url: ``str``
    """
    _releases = requests.get(url)
    loaded_releases = _releases.json()
    releases = list()
    for i in loaded_releases:
        for k, v in i.iteritems():
            if k == 'name':
                # if the name is not excluded append it
                if not any([v.startswith(i) for i in EXCLUDE]):
                    releases.append(v)
    else:
        # Return a unique list.
        return list(set(releases))

all_releases = list()
all_releases.extend(return_releases(url="${GITHUB_API_ENDPOINT}/tags"))
all_releases.extend(return_releases(url="${GITHUB_API_ENDPOINT}/branches"))
print(' '.join(all_releases))
EOF
)
fi


function cleanup() {
    # Ensure workspaces are cleaned up
    rm -rf /tmp/rpc_wheels*
    rm -rf /tmp/pip*
    rm -rf "${WORK_DIR}"    
}


# Iterate through the list of releases and build everything that's needed
for release in ${RELEASES}; do

    # Perform cleanup
    cleanup

    # Git clone repo
    git clone "${GIT_REPO}" "${WORK_DIR}"

    # checkout release
    pushd "${WORK_DIR}"
      git checkout "${release}"
    popd

    # Build wheels
    /opt/rpc-wheel-builder.py -i "${REPO_PACKAGES_PATH}" \
                              -o "${OUTPUT_WHEEL_PATH}"/pools \
                              --link-dir "${OUTPUT_WHEEL_PATH}"/"${release}" \
                              --git-repos "${OUTPUT_GIT_PATH}" \
                              --release "${release}"
done

# Perform cleanup
cleanup
