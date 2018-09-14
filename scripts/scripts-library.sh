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


## Vars ----------------------------------------------------------------------
LINE='----------------------------------------------------------------------'
MAX_RETRIES=${MAX_RETRIES:-5}
ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:--e gather_facts=False}
STARTTIME="${STARTTIME:-$(date +%s)}"
COMMAND_LOGS=${COMMAND_LOGS:-"/openstack/log/ansible_cmd_logs"}

# The default SSHD configuration has MaxSessions = 10. If a deployer changes
#  their SSHD config, then the ANSIBLE_FORKS may be set to a higher number. We
#  set the value to 10 or the number of CPU's, whichever is less. This is to
#  balance between performance gains from the higher number, and CPU
#  consumption. If ANSIBLE_FORKS is already set to a value, then we leave it
#  alone.
#  ref: https://bugs.launchpad.net/openstack-ansible/+bug/1479812
if [ -z "${ANSIBLE_FORKS:-}" ]; then
  CPU_NUM=$(grep -c ^processor /proc/cpuinfo)
  if [ ${CPU_NUM} -lt "10" ]; then
    ANSIBLE_FORKS=${CPU_NUM}
  else
    ANSIBLE_FORKS=10
  fi
fi


## Functions -----------------------------------------------------------------
# Determine the distribution we are running on, so that we can configure it
# appropriately.
function determine_distro {
    source /etc/os-release 2>/dev/null
    export DISTRO_ID="${ID}"
    export DISTRO_NAME="${NAME}"
    export DISTRO_VERSION_ID="${VERSION_ID}"
}

# Used to retry a process that may fail due to random issues.
function successerator {
  set +e
  # Get the time that the method was started.
  OP_START_TIME=$(date +%s)
  # Set the initial return value to failure.
  false
  for ((RETRY=0; $? != 0 && RETRY < MAX_RETRIES; RETRY++)); do
    if [ ${RETRY} -gt 1 ];then
      "$@" -vvvv
    else
      "$@"
    fi
  done
  # If max retires were hit, fail.
  if [ $? -ne 0 ] && [ ${RETRY} -eq ${MAX_RETRIES} ];then
    echo -e "\nHit maximum number of retries, giving up...\n"
    exit_fail
  fi
  # Ensure the log directory exists
  if [[ ! -d "${COMMAND_LOGS}" ]];then
    mkdir -p "${COMMAND_LOGS}"
  fi
  # Log the time that the method completed.
  OP_TOTAL_SECONDS="$(( $(date +%s) - OP_START_TIME ))"
  echo -e "- Operation: [ $@ ]\t${OP_TOTAL_SECONDS} seconds\tNumber of Attempts [ ${RETRY} ]" \
    >> ${COMMAND_LOGS}/ansible_runtime_report.txt
  set -e
}

function install_bits {
  # Use the successerator to run openstack-ansible
  successerator openstack-ansible "$@" ${ANSIBLE_PARAMETERS}
}

function ssh_key_create {
  # Ensure that the ssh key exists and is an authorized_key
  key_path="${HOME}/.ssh"
  key_file="${key_path}/id_rsa"

  # Ensure that the .ssh directory exists and has the right mode
  if [ ! -d ${key_path} ]; then
    mkdir -p ${key_path}
    chmod 700 ${key_path}
  fi

  # Ensure a full keypair exists
  if [ ! -f "${key_file}" -o ! -f "${key_file}.pub" ]; then

    # Regenrate public key if private key exists
    if [ -f "${key_file}" ]; then
      ssh-keygen -f ${key_file} -y > ${key_file}.pub
    fi

    # Delete public key if private key missing
    if [ ! -f "${key_file}" ]; then
      rm -f ${key_file}.pub
    fi

    # Regenerate keypair if both keys missing
    if [ ! -f "${key_file}" -a ! -f "${key_file}.pub" ]; then
      ssh-keygen -t rsa -f ${key_file} -N ''
    fi

  fi

  # Ensure that the public key is included in the authorized_keys
  # for the default root directory and the current home directory
  key_content=$(cat "${key_file}.pub")
  if ! grep -q "${key_content}" ${key_path}/authorized_keys; then
    echo "${key_content}" | tee -a ${key_path}/authorized_keys
  fi
}

function exit_state {
  set +x
  TOTALSECONDS="$(( $(date +%s) - STARTTIME ))"
  info_block "Run Time = ${TOTALSECONDS} seconds || $((TOTALSECONDS / 60)) minutes"
  if [ "${1}" == 0 ];then
    info_block "Status: Success"
  else
    info_block "Status: Failure"
  fi
  exit ${1}
}

function exit_success {
  set +x
  exit_state 0
}

function exit_fail {
  set +x
  log_instance_info
  info_block "Error Info - $@"
  exit_state 1
}

function gate_job_exit_tasks {
  # If this is a gate node from OpenStack-Infra Store all logs into the
  #  execution directory after gate run.
  if [[ -d "/etc/nodepool" ]];then
    GATE_LOG_DIR="$(dirname "${0}")/../logs"
    mkdir -p "${GATE_LOG_DIR}/host" "${GATE_LOG_DIR}/openstack"
    rsync --archive --verbose --safe-links --ignore-errors /var/log/ "${GATE_LOG_DIR}/host" || true
    rsync --archive --verbose --safe-links --ignore-errors /openstack/log/ "${GATE_LOG_DIR}/openstack" || true
    # Rename all files gathered to have a .txt suffix so that the compressed
    # files are viewable via a web browser in OpenStack-CI.
    # except tempest results testrepository.subunit and testr_results.html
    find "${GATE_LOG_DIR}/" -type f -not -name "testrepository.subunit" -not -name "testr_results.html" -exec mv {} {}.txt \;
    # Compress the files gathered so that they do not take up too much space.
    # We use 'command' to ensure that we're not executing with some sort of alias.
    command gzip --best --recursive "${GATE_LOG_DIR}/"
    # Ensure that the files are readable by all users, including the non-root
    # OpenStack-CI jenkins user.
    chmod -R 0777 "${GATE_LOG_DIR}"
  fi
}

function print_info {
  PROC_NAME="- [ $@ ] -"
  printf "\n%s%s\n" "$PROC_NAME" "${LINE:${#PROC_NAME}}"
}

function info_block {
  echo "${LINE}"
  print_info "$@"
  echo "${LINE}"
}

function log_instance_info {
  set +x
  # Get host information post initial setup and reset verbosity
  if [ ! -d "/openstack/log/instance-info" ];then
    mkdir -p "/openstack/log/instance-info"
  fi
  get_instance_info
  set -x
}

function get_repos_info {
  for i in /etc/apt/sources.list /etc/apt/sources.list.d/* /etc/yum.conf /etc/yum.repos.d/*; do
    if [ -f "${i}" ]; then
      echo -e "\n$i"
      cat $i
    fi
  done
}

# Get instance info
function get_instance_info {
  TS="$(date +"%H-%M-%S")"
  (cat /etc/resolv.conf && \
    which systemd-resolve && \
      systemd-resolve --statistics && \
        cat /etc/systemd/resolved.conf) > \
          "/openstack/log/instance-info/host_dns_info_${TS}.log" || true
  tracepath "8.8.8.8" -m 5 > \
    "/openstack/log/instance-info/host_tracepath_info_${TS}.log" || true
  tracepath6 "2001:4860:4860::8888" -m 5 >> \
    "/openstack/log/instance-info/host_tracepath_info_${TS}.log" || true
  lxc-ls --fancy > \
    "/openstack/log/instance-info/host_lxc_container_info_${TS}.log" || true
  lxc-checkconfig > \
    "/openstack/log/instance-info/host_lxc_config_info_${TS}.log" || true
  (iptables -vnL && iptables -t nat -vnL && iptables -t mangle -vnL) > \
    "/openstack/log/instance-info/host_firewall_info_${TS}.log" || true
  ANSIBLE_HOST_KEY_CHECKING=False \
    ansible -i "localhost," localhost -m setup > \
      "/openstack/log/instance-info/host_system_info_${TS}.log" || true
  get_repos_info > \
    "/openstack/log/instance-info/host_repo_info_${TS}.log" || true

  determine_distro
  case ${DISTRO_ID} in
      centos|rhel|fedora)
          rpm -qa > \
            "/openstack/log/instance-info/host_packages_info_${TS}.log" || true
          ;;
      ubuntu|debian)
          dpkg-query --list > \
            "/openstack/log/instance-info/host_packages_info_${TS}.log" || true
          ;;
  esac
}

function print_report {
  # Print the stored report data
  cat ${COMMAND_LOGS}/ansible_runtime_report.txt
}

function get_pip {
  # The python executable to use when executing get-pip is passed
  # as a parameter to this function.
  GETPIP_PYTHON_EXEC_PATH="${1:-$(which python)}"

  # Download the get-pip script using the primary or secondary URL
  GETPIP_FILE="/opt/get-pip.py"
  GETPIP_CMD="curl --fail --silent --show-error --retry 5 --output ${GETPIP_FILE}"
  # If GET_PIP_URL is set, then just use it
  if [ -n "${GET_PIP_URL:-}" ]; then
    ${GETPIP_CMD} ${GET_PIP_URL}
  else
    # Otherwise, try the two standard URL's
    ${GETPIP_CMD} https://bootstrap.pypa.io/3.3/get-pip.py \
      || ${GETPIP_CMD} https://raw.githubusercontent.com/pypa/get-pip/master/3.3/get-pip.py
  fi

  ${GETPIP_PYTHON_EXEC_PATH} ${GETPIP_FILE} \
    pip setuptools wheel \
    --constraint global-requirement-pins.txt \
    || ${GETPIP_PYTHON_EXEC_PATH} ${GETPIP_FILE} \
         pip setuptools wheel \
         --constraint global-requirement-pins.txt \
         --isolated
}

## Signal traps --------------------------------------------------------------
# Trap all Death Signals and Errors
trap "exit_fail ${LINENO} $? 'Received STOP Signal'" SIGHUP SIGINT SIGTERM
trap "exit_fail ${LINENO} $?" ERR

## Pre-flight check ----------------------------------------------------------
# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
  info_block "This script must be run as root"
  exit_state 1
fi

# Check that we are in the root path of the cloned repo
if [ ! -d "etc" -a ! -d "scripts" -a ! -d "playbooks" ]; then
  info_block "** ERROR **"
  echo "Please execute this script from the root directory of the cloned source code."
  echo -e "Example: /opt/openstack-ansible/\n"
  exit_state 1
fi


## Exports -------------------------------------------------------------------
# Export known paths
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}"

# Export the home directory just in case it's not set
export HOME="/root"

if [[ -f "/usr/local/bin/openstack-ansible.rc" ]];then
  source "/usr/local/bin/openstack-ansible.rc"
fi
