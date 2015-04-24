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

# What this script is for:
#   This script updates the various "rpc_release" variables The purpose of
#   this script is to eliminate error when updating the released versions.

if echo "$@" | grep -e '-h' -e '--help' || [ -z "${2}" ];then
    echo "
Options:
  -r|--revision       (name/id of revision)
"
exit 0
fi

# Provide some CLI options
while [[ $# > 1 ]]
do
key="$1"
case $key in
    -r|--revision)
    REVISION="$2"
    shift
    ;;
    *)
    ;;
esac
shift
done

sed -i '' "s/^rpc_release\:.*/rpc_release\: ${REVISION}/" rpc_deployment/inventory/group_vars/all.yml
sed -i '' "s/^git_install_branch\:.*/git_install_branch\: ${REVISION}/" rpc_deployment/vars/repo_packages/raxmon_agent.yml
