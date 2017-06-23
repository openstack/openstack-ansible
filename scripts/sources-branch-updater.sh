#!/usr/bin/env bash
# Copyright 2015, Rackspace US, Inc.
# Copyright 2017, SUSE LINUX GmbH.
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

# This script was created to rapidly interate through a repo_package file
# that contains git sources and set the various repositories inside to
# the head of given branch via the SHA. This makes it possible to update
# all of the services that we support in an "automated" fashion.

OS_BRANCH=${OS_BRANCH:-"master"}
OSA_BRANCH=${OSA_BRANCH:-"$OS_BRANCH"}
SERVICE_FILE=${SERVICE_FILE:-"playbooks/defaults/repo_packages/openstack_services.yml"}
OPENSTACK_SERVICE_LIST=${OPENSTACK_SERVICE_LIST:-"$(grep 'git_repo\:' ${SERVICE_FILE} | awk -F '/' '{ print $NF }' | egrep -v 'requirements|-' | tr '\n' ' ')"}
PRE_RELEASE=${PRE_RELEASE:-"false"}
FORCE_MASTER=${FORCE_MASTER:-"false"}

source scripts/sources-branch-updater-lib.sh || { echo "Failed to source updater library"; exit 1; }

if echo "$@" | grep -e '-h' -e '--help';then
    echo "
Options:
  -b|--openstack-branch (name of OpenStack branch, eg: stable/newton)
  -o|--osa-branch       (name of the OSA branch, eg: stable/newton)
  -s|--service-file     (path to service file to parse)
"
exit 0
fi

# Provide some CLI options
while [[ $# > 1 ]]; do
key="$1"
case $key in
    -b|--openstack-branch)
    OS_BRANCH="$2"
    shift
    ;;
    -o|--osa-branch)
    OSA_BRANCH="$2"
    shift
    ;;
    -s|--service-file)
    SERVICE_FILE="$2"
    shift
    ;;
    *)
    ;;
esac
shift
done

commit_changes() {
  local repo_name="${1}"
  local osa_repo_tmp_path="/tmp/osa_${repo_name}"

  # Switch into the OSA git directory to work with it
  pushd ${osa_repo_tmp_path} > /dev/null

  # Check for changed files
  git_changed=$(git status --porcelain | wc -l)
  # Check for untracked files
  git_untracked=$(git ls-files --other --exclude-standard --directory | wc -l)
  if [ ${git_untracked} -gt 0 ]; then
    # If there are untracked files, ensure that the commit message includes
    # a WIP prefix so that the patch is revised in more detail.
    git_msg_prefix="[New files - needs update] "
  else
    git_msg_prefix=""
  fi

  # If any files have changed, submit a patch including the changes
  if [ ${git_changed} -gt 0 ]; then
    git checkout -b sha-update
    git review -s > /dev/null
    git add --all
    git commit -a -m "${git_msg_prefix}Update paste, policy and rootwrap configurations $(date +%Y-%m-%d)" --quiet
    git review > /dev/null
  fi
  popd > /dev/null
}

osa_post_sync_hook() { commit_changes "$@"; }

sync_roles_and_packages ${OS_BRANCH} ${OSA_BRANCH} ${SERVICE_FILE} ${OPENSTACK_SERVICE_LIST}

update_pip_options

update_ansible_role_requirements ${OSA_BRANCH} ${PRE_RELEASE} ${FORCE_MASTER}

update_release_version ${OSA_BRANCH} ${SERVICE_FILE}
