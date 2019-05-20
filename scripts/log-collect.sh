#!/usr/bin/env bash

# Copyright 2016, Rackspace US, Inc.
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

# WARNING:
# This file is use by all OpenStack-Ansible roles for testing purposes.
# Any changes here will affect all OpenStack-Ansible role repositories
# with immediate effect.

# PURPOSE:
# This script collects, renames and compresses the logs produced in
# a role test if the host is in OpenStack-CI.

## Vars ----------------------------------------------------------------------
export WORKING_DIR=${WORKING_DIR:-$(pwd)}
export RUN_ARA=${RUN_ARA:-false}
export TESTING_HOME=${TESTING_HOME:-$HOME}
export TS=$(date +"%H-%M-%S")

export RSYNC_CMD="rsync --archive --copy-links --ignore-errors --quiet --no-perms --no-owner --no-group --whole-file --inplace"

# NOTE(cloudnull): This is a very simple list of common directories in /etc we
#                  wish to search for when storing gate artifacts. When adding
#                  things to this list please alphabetize the entries so it's
#                  easy for folks to find and adjust items as needed.
COMMON_ETC_LOG_NAMES="apt \
    apache2 \
    calico \
    haproxy \
    httpd \
    memcached \
    mongodb \
    my.cnf \
    mysql \
    netplan \
    network \
    nginx \
    openstack_deploy \
    pip.conf \
    qpid-dispatch \
    rabbitmq \
    repo \
    resolv.conf \
    rsyslog \
    sasl2 \
    sysconfig/network-scripts \
    sysconfig/network \
    systemd/network \
    yum \
    yum.repos.d \
    zypp"

COMMON_ETC_LOG_NAMES+=" $(awk -F'os_' '/name.*os_.*/ {print $2}' $(dirname $(readlink -f ${BASH_SOURCE[0]}))/../ansible-role-requirements.yml | tr '\n' ' ')"

## Functions -----------------------------------------------------------------

function repo_information {
    [[ "${1}" != "host" ]] && lxc_cmd="lxc-attach --name ${1} --" || lxc_cmd=""
    echo "Collecting list of installed packages and enabled repositories for \"${1}\""
    # Redhat package debugging
    if eval sudo ${lxc_cmd} which yum &>/dev/null || eval sudo ${lxc_cmd} which dnf &>/dev/null; then
        # Prefer dnf over yum for CentOS.
        eval sudo ${lxc_cmd} which dnf &>/dev/null && RHT_PKG_MGR='dnf' || RHT_PKG_MGR='yum'
        eval sudo ${lxc_cmd} $RHT_PKG_MGR repolist -v > "${WORKING_DIR}/logs/redhat-rpm-repolist-${1}-${TS}.txt" || true
        eval sudo ${lxc_cmd} $RHT_PKG_MGR list installed > "${WORKING_DIR}/logs/redhat-rpm-list-installed-${1}-${TS}.txt" || true

    # SUSE package debugging
    elif eval sudo ${lxc_cmd} which zypper &>/dev/null; then
        eval sudo ${lxc_cmd} zypper lr -d > "${WORKING_DIR}/logs/suse-zypper-repolist-${1}-${TS}.txt" || true
        eval sudo ${lxc_cmd} zypper --disable-repositories pa -i > "${WORKING_DIR}/logs/suse-zypper-list-installed-${1}-${TS}.txt" || true

    # Ubuntu package debugging
    elif eval sudo ${lxc_cmd} which apt-get &> /dev/null; then
        eval sudo ${lxc_cmd} apt-cache policy | grep http | awk '{print $1" "$2" "$3}' | sort -u > "${WORKING_DIR}/logs/ubuntu-apt-repolist-${1}-${TS}.txt" || true
        eval sudo ${lxc_cmd} apt list --installed > "${WORKING_DIR}/logs/ubuntu-apt-list-installed-${1}-${TS}.txt" || true

    # Gentoo package debugging
    elif eval sudo ${lxc_cmd} which emerge &> /dev/null; then
        # list installed packages
        eval sudo ${lxc_cmd} equery list "*" > "${WORKING_DIR}/logs/gentoo-portage-list-installed-${1}-${TS}.txt" || true
        # list only packages called for install (not dependancies)
        eval sudo ${lxc_cmd} cat /var/lib/portage/world > "${WORKING_DIR}/logs/gentoo-portage-list-manual-installed-${1}-${TS}.txt" || true
    fi

}

function store_artifacts {
    # Store known artifacts only if they exist. If the target directory does
    # exist, it will be created.
    # USAGE: store_artifacts /src/to/artifacts /path/to/store
    if sudo test -e "${1}"; then
        if [[ ! -d "${2}" ]]; then
            mkdir -vp "${2}"
        fi
        echo "Running artifact sync for \"${1}\" to \"${2}\""
        sudo ${RSYNC_CMD} ${1} ${2} || true
    fi
}

function store_journal_artifacts {
    # Store lines from a known unit's journal as a plain-text log file.
    # USAGE: store_journal_artifacts UNIT_TO_MATCH /path/to/store
    if [ $? == 0 ]; then
        if [[ ! -d "${2}" ]]; then
            mkdir -vp "${2}"
        fi
        if [[ ${3:-false} != false ]]; then
            if [[ -f "${3}/system.journal" ]]; then
                SYSTEMD_UNITS=$(sudo journalctl --file="${3}/system.journal" -F _SYSTEMD_UNIT | grep "${service}")
                for service_unit in $(echo -e "${SYSTEMD_UNITS}"); do
                    echo "Pulling journal for ${service_unit}"
                    sudo journalctl --file="${3}/system.journal" \
                                    --unit="${service_unit}" | sudo tee "${2}/${service_unit}.journal-${TS}.log" &>/dev/null
                done
            fi
        else
            SYSTEMD_UNITS=$(sudo journalctl --output=json-pretty -F _SYSTEMD_UNIT | grep "${service}")
            for service_unit in $(echo -e "${SYSTEMD_UNITS}"); do
                echo "Pulling journal for ${service_unit}"
                sudo journalctl --unit="${service_unit}" | sudo tee "${2}/${service_unit}.journal-${TS}.log" &>/dev/null
            done
        fi
    fi
}

function find_files {
    find "${WORKING_DIR}/logs/" -type f \
        ! -name "*.gz" \
        ! -name '*.html' \
        ! -name '*.subunit' \
        ! -name "*.journal" \
        ! -name 'ansible.sqlite' | grep -v 'stackviz'
}

function rename_files {
    find_files |\
        while read filename; do \
            mv ${filename} ${filename}.txt || echo "WARNING: Could not rename ${filename}"; \
        done
}

function compress_files {
    # We use 'command' to ensure that we're not executing with an alias.
    GZIP_CMD="command gzip --force --best"
    find_files |\
        while read filename; do \
            ${GZIP_CMD} ${filename} || echo "WARNING: Could not gzip ${filename}"; \
        done
}

## Main ----------------------------------------------------------------------

echo "#### BEGIN LOG COLLECTION ###"

mkdir -vp "${WORKING_DIR}/logs"

# Gather basic logs
store_artifacts /openstack/log/ansible-logging/ "${WORKING_DIR}/logs/ansible"
store_artifacts /openstack/log/ "${WORKING_DIR}/logs/openstack"
store_artifacts /var/log/ "${WORKING_DIR}/logs/host"

# Store the ara sqlite database in the openstack-ci expected path
store_artifacts "${TESTING_HOME}/.ara/ansible.sqlite" "${WORKING_DIR}/logs/ara-report/"

# Store netstat report
store_artifacts /tmp/listening_port_report.txt "${WORKING_DIR}/logs/host"

# Copy the repo os-releases *.txt files
# container path
store_artifacts /openstack/*repo*/repo/os-releases/*/*/*.txt "${WORKING_DIR}/repo"

# metal path
store_artifacts /var/www/repo/os-releases/*/*/*.txt "${WORKING_DIR}/repo"

# Verify the integrity of the journal files but do not fail if one of them is not usable
echo "Verifying journal files consistency..."
find /var/log/journal/ -type f -name "*.journal" -exec bash -c 'sudo journalctl --file={} --verify || true' \;


# Gather host etc artifacts
PIDS=()
for service in ${COMMON_ETC_LOG_NAMES}; do
    echo "Running collection for service ${service}"
    store_artifacts "/etc/${service}" "${WORKING_DIR}/logs/etc/host/" &
    pid=$!
    PIDS[${pid}]=${pid}
    store_journal_artifacts "${service}" "${WORKING_DIR}/logs/host" &
    pid=$!
    PIDS[${pid}]=${pid}
done
echo "Waiting for host collection jobs to finish"
for job_pid in ${!PIDS[@]}; do
    wait ${PIDS[$job_pid]} || exit 99
done


# Gather container etc artifacts
if which lxc-ls &> /dev/null; then
    for CONTAINER_NAME in $(sudo lxc-ls -1); do
        CONTAINER_PID=$(sudo lxc-info -p -n ${CONTAINER_NAME} | awk '{print $2}')
        ETC_DIR="/proc/${CONTAINER_PID}/root/etc"
        MACHINE_ID="$(sudo cat ${ETC_DIR}/machine-id)"
        LOG_DIR="/proc/${CONTAINER_PID}/root/var/log"
        JOURNAL_DIR="/proc/${CONTAINER_PID}/root/run/log/journal/${MACHINE_ID}"
        repo_information ${CONTAINER_NAME}
        PIDS=()
        for service in ${COMMON_ETC_LOG_NAMES}; do
            echo "Running in container collection for service ${service}"
            store_artifacts ${ETC_DIR}/${service} "${WORKING_DIR}/logs/etc/openstack/${CONTAINER_NAME}/" &
            pid=$!
            PIDS[${pid}]=${pid}
            store_artifacts ${LOG_DIR}/${service} "${WORKING_DIR}/logs/openstack/${CONTAINER_NAME}/" &
            pid=$!
            PIDS[${pid}]=${pid}
            store_journal_artifacts ${service} "${WORKING_DIR}/logs/openstack/${CONTAINER_NAME}" "${JOURNAL_DIR}" &
            pid=$!
            PIDS[${pid}]=${pid}
        done
        echo "Waiting for container collection jobs for ${CONTAINER_NAME} to finish"
        for job_pid in ${!PIDS[@]}; do
            wait ${PIDS[$job_pid]} || exit 99
        done
    done
fi


# Rename all files gathered to have a .txt suffix so that the compressed
# files are viewable via a web browser in OpenStack-CI.
rename_files

# If we could not find ARA, assume it was not installed
# and skip all the related activities.
if [ "${RUN_ARA}" = true ]; then
    # Generate the ARA subunit report so that the
    # results reflect in OpenStack-Health
    mkdir -vp "${WORKING_DIR}/logs/ara-data"
    echo "Generating ARA report subunit report."
    /opt/ansible-runtime/bin/ara generate subunit "${WORKING_DIR}/logs/ara-data/testrepository.subunit" || true
fi

# Get a dmesg output so we can look for kernel failures
dmesg > "${WORKING_DIR}/logs/dmesg-${TS}.txt" || true

# Collect job environment
env > "${WORKING_DIR}/logs/environment-${TS}.txt"  || true

repo_information host

# Record the active interface configs
if which ethtool &> /dev/null; then
    for interface in $(ip -o link | awk -F':' '{print $2}' | sed 's/@.*//g'); do
        echo "ethtool -k ${interface}"
        ethtool -k ${interface} > "${WORKING_DIR}/logs/ethtool-${interface}-${TS}-cfg.txt" || true
    done
else
    echo "No ethtool available" | tee -a "${WORKING_DIR}/logs/ethtool-${TS}-${interface}-cfg.txt"
fi

# Compress the files gathered so that they do not take up too much space.
compress_files

# Ensure that the files are readable by all users, including the non-root
# OpenStack-CI jenkins user.
sudo chmod -R ugo+rX "${WORKING_DIR}/logs"
sudo chown -R $(whoami) "${WORKING_DIR}/logs"

echo "#### END LOG COLLECTION ###"

