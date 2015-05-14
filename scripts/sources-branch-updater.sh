#!/usr/bin/env bash
# Copyright 2015, Rackspace US, Inc.
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

ONLINE_BRANCH=${ONLINE_BRANCH:-"stable/kilo"}
SERVICE_FILE=${SERVICE_FILE:-"playbooks/defaults/repo_packages/openstack_services.yml"}

IFS=$'\n'

if echo "$@" | grep -e '-h' -e '--help';then
    echo "
Options:
  -b|--branch       (name of branch)
  -s|--service-file (path to service file to parse)
"
exit 0
fi

# Provide some CLI options
while [[ $# > 1 ]]
do
key="$1"
case $key in
    -b|--branch)
    ONLINE_BRANCH="$2"
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

# Iterate through the service file
for repo in $(grep 'git_repo\:' ${SERVICE_FILE});do
  # Set the repo name
  repo_name=$(echo "${repo}" | sed 's/_git_repo\:.*//g')
  # Get the branch data
  branch_data=$(git ls-remote "$(echo ${repo} | awk '{print $2}')" | grep "${ONLINE_BRANCH}$")

  # If there is branch data continue
  if [ ! -z "${branch_data}" ];then
    # Set the branch sha for the head of the branch
    branch_sha=$(echo "${branch_data}" | awk '{print $1}')
    # Set the branch entry
    branch_entry="${branch_sha} # HEAD of \"$ONLINE_BRANCH\" as of $(date +%d.%m.%Y)"
    # Write the branch entry
    sed -i '' "s|${repo_name}_git_install_branch:.*|${repo_name}_git_install_branch: $branch_entry|" ${SERVICE_FILE}
    echo "processed $repo_name @ $branch_entry"
  fi
done
