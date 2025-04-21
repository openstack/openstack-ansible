#!/bin/bash

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

# Get list of all the maintained OpenStack Ansible projects

# 'exclude_projects' variable should contain all the OSA projects
# listed in https://opendev.org/ but should be excluded
# from the generated list for various reasons (ie unmaintained,
# not applicable etc)

# Do not leave empty lines since grep -F will not match anything

set -e

exclude_project() {
    excluded_projects+="openstack/$1 "
}

extra_include_project() {
    extra_included_projects+="openstack/$1 "
}

############## EXCLUDED PROJECTS ######################
#
# List of the projects that need to be excluded for various
# reasons
#
# retired projects
exclude_project openstack-ansible-os_freezer
exclude_project openstack-ansible-os_swift_sync
exclude_project openstack-ansible-pip_lock_down
exclude_project openstack-ansible-py_from_git
exclude_project openstack-ansible-security
# integrated is where we are so we know it's maintained
exclude_project openstack-ansible
#
############## END OF EXCLUDED PROJECTS ###############

############## INCLUDED PROJECTS ######################
#
# List of additional projects that need to be included for various
# reasons
#
# ansible-hardening. Used by AIO in favor of the retired
# openstack-ansible-security
extra_include_project ansible-config_template
extra_include_project ansible-hardening
extra_include_project ansible-role-python_venv_build
extra_include_project ansible-role-systemd_mount
extra_include_project ansible-role-systemd_networkd
extra_include_project ansible-role-systemd_service
############## END OF INCLUDED PROJECTS ###############

# Replace spaces with newlines as expected by grep -F
excluded_projects="$(echo ${excluded_projects} | tr ' ' '\n')"

# The output should only contain a list of projects or an empty string.
# Anything else will probably make the CI bots to fail.

ssh -p 29418 proposal-bot@review.opendev.org gerrit ls-projects --prefix openstack/openstack-ansible- | \
    grep -v -F "${excluded_projects}" | uniq | sort -n

for x in ${extra_included_projects[@]}; do
    echo $x
done
