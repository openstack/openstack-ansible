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
exclude_project openstack-ansible-galera_client
exclude_project openstack-ansible-nspawn_hosts
exclude_project openstack-ansible-nspawn_container_create
exclude_project openstack-ansible-os_almanach
exclude_project openstack-ansible-os_congress
exclude_project openstack-ansible-os_karbor
exclude_project openstack-ansible-os_molteniron
exclude_project openstack-ansible-os_monasca
exclude_project openstack-ansible-os_monasca-agent
exclude_project openstack-ansible-os_monasca-ui
exclude_project openstack-ansible-os_murano
exclude_project openstack-ansible-os_panko
exclude_project openstack-ansible-os_sahara
exclude_project openstack-ansible-os_searchlight
exclude_project openstack-ansible-os_senlin
exclude_project openstack-ansible-os_swift_sync
exclude_project openstack-ansible-os_zaqar
exclude_project openstack-ansible-pip_install
exclude_project openstack-ansible-pip_lock_down
exclude_project openstack-ansible-py_from_git
exclude_project openstack-ansible-repo_build
exclude_project openstack-ansible-rsyslog_client
exclude_project openstack-ansible-rsyslog_server
exclude_project openstack-ansible-security

############## END OF EXCLUDED PROJECTS ###############

############## INCLUDED PROJECTS ######################
#
# List of additional projects that need to be included for various
# reasons
#
extra_include_project ansible-config_template
extra_include_project ansible-hardening
extra_include_project ansible-role-frrouting
extra_include_project ansible-role-httpd
extra_include_project ansible-role-pki
extra_include_project ansible-role-python_venv_build
extra_include_project ansible-role-systemd_mount
extra_include_project ansible-role-systemd_networkd
extra_include_project ansible-role-systemd_service
extra_include_project ansible-role-uwsgi
extra_include_project ansible-role-zookeeper
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
