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

## Shell Opts ----------------------------------------------------------------
set -e -u -v

export SCRIPTS_PATH="${SCRIPTS_PATH:-$(dirname $(dirname $(dirname $(readlink -f $0))))}"

# If there is a pip config found remove it
if [ -d "$HOME/.pip" ];then
  tar -czf ~/pre-upgrade-pip-directory.tgz ~/.pip
  rm -rf ~/.pip
fi

# Upgrade ansible in place
${SCRIPTS_PATH}/bootstrap-ansible.sh
