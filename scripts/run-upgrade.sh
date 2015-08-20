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

# NOTICE: To run this in an automated fashion run the script via
#   root@HOSTNAME:/opt/openstack-ansible# echo "YES" | bash scripts/run-upgrade.sh


## Shell Opts ----------------------------------------------------------------
set -e -u -v

## Functions -----------------------------------------------------------------

function check_for_juno {
    if [ -d "/etc/rpc_deploy" ];then
      echo "--------------ERROR--------------"
      echo "/etc/rpc_deploy directory found, which looks like you're trying to upgrade from Juno."
      echo "Please upgrade your environment to Kilo before proceeding."
      exit 1
    fi
}


function check_for_kilo {
    if [[ ! -d "/etc/openstack_deploy" ]]; then
      echo "--------------ERROR--------------"
      echo "/etc/openstack_deploy directory not found."
      echo "It appears you do not have a Kilo environment installed."
      exit 2
    fi
}

function pre_flight {
    ## Library Check -------------------------------------------------------------
    echo "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh
    ## Pre-flight Check ----------------------------------------------------------
    # Clear the screen and make sure the user understands whats happening.
    clear

    # Notify the user.
    echo -e "
    This script will perform a v11.x to v12.x upgrade.
    Once you start the upgrade there's no going back.

    Note, this is an online upgrade and while the
    in progress running VMs will not be impacted.
    However, you can expect some hiccups with OpenStack
    API services while the upgrade is running.

    Are you ready to perform this upgrade now?
    "

    # Confirm the user is ready to upgrade.
    read -p 'Enter "YES" to continue or anything else to quit: ' UPGRADE
    if [ "${UPGRADE}" == "YES" ]; then
      echo "Running Upgrade from v11.x to v12.x"
    else
      exit 99
    fi
}


## Main ----------------------------------------------------------------------

function main {
    pre_flight
    check_for_juno
    check_for_kilo
}

main
