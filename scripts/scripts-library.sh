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
ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-""}
STARTTIME="${STARTTIME:-$(date +%s)}"
COMMAND_LOGS=${COMMAND_LOGS:-"/openstack/log/ansible_cmd_logs"}

# The vars used to prepare the Ansible runtime venv
PIP_COMMAND="/opt/ansible-runtime/bin/pip"

ZUUL_PROJECT="${ZUUL_PROJECT:-}"
GATE_EXIT_LOG_COPY="${GATE_EXIT_LOG_COPY:-false}"
GATE_EXIT_LOG_GZIP="${GATE_EXIT_LOG_GZIP:-true}"
GATE_EXIT_RUN_ARA="${GATE_EXIT_RUN_ARA:-true}"

if [ -v ZUUL_PROJECT ] || [ -v ZUUL_SRC_PATH ]; then
  GATE_EXIT_RUN_DSTAT="${GATE_EXIT_RUN_DSTAT:-true}"
else
  GATE_EXIT_RUN_DSTAT="${GATE_EXIT_RUN_DSTAT:-false}"
fi

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
# Build ansible-runtime venv
function build_ansible_runtime_venv {
    # All distros have a python-virtualenv > 13.
    # - Centos 8 Stream has 15.1, which holds pip 9.0.1, setuptools 28.8, wheel 0.29
    # - openSUSE 42.3 has 13.1.2, which holds pip 7.1.2, setuptools 18.2, wheel 0.24.
    #   See also: https://build.opensuse.org/package/show/openSUSE%3ALeap%3A42.3/python-virtualenv
    # - Ubuntu Xenial has 15.0.1, holding pip 8.1.1, setuptools 20.3, wheel 0.29
    #   See also: https://packages.ubuntu.com/xenial/python-virtualenv

    ${PYTHON_EXEC_PATH} -m venv /opt/ansible-runtime --clear

    # The vars used to prepare the Ansible runtime venv
    PIP_OPTS+=" --constraint global-requirement-pins.txt"

    # When executing the installation, we want to specify all our options on the CLI,
    # making sure to completely ignore any config already on the host. This is to
    # prevent the repo server's extra constraints being applied, which include
    # a different version of Ansible to the one we want to install. As such, we
    # use --isolated so that the config file is ignored.

    # Upgrade pip setuptools and wheel to the appropriate version
    ${PIP_COMMAND} install --isolated ${PIP_OPTS} --constraint ${TOX_CONSTRAINTS_FILE} --upgrade pip setuptools wheel

    # Install ansible and the other required packages
    ${PIP_COMMAND} install --isolated ${PIP_OPTS} --constraint ${TOX_CONSTRAINTS_FILE} -r requirements.txt ${ANSIBLE_PACKAGE}

    # Install our osa_toolkit code from the current checkout
    $PIP_COMMAND install -e .

    # If we are in openstack-CI, install systemd-python for the log collection python script
    if [[ -e /etc/ci/mirror_info.sh ]]; then
      ${PIP_COMMAND} install --isolated ${PIP_OPTS} systemd-python
    fi
}

# If in OpenStack-Infra, set some vars to use the mirror when bootstrapping Ansible
function load_nodepool_pip_opts {
    if [[ -e /etc/ci/mirror_info.sh ]]; then
        source /etc/ci/mirror_info.sh
        export PIP_OPTS="--index-url ${NODEPOOL_PYPI_MIRROR} --trusted-host ${NODEPOOL_MIRROR_HOST} --extra-index-url ${NODEPOOL_WHEEL_MIRROR}"
    fi
}

# Determine the distribution we are running on, so that we can configure it
# appropriately.
function determine_distro {
    source /etc/os-release 2>/dev/null
    export DISTRO_ID="${ID}"
    export DISTRO_NAME="${NAME}"
    export DISTRO_VERSION_ID=${VERSION_ID}
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
  if [ "$GATE_EXIT_RUN_DSTAT" == true ]; then
    generate_dstat_charts || true
  fi
  exit_state 0
}

function exit_fail {
  set +x
  if [ "$GATE_EXIT_RUN_DSTAT" == true ]; then
    generate_dstat_charts || true
  fi
  info_block "Error Info - $@"
  exit_state 1
}

function gate_job_exit_tasks {
  # This environment variable captures the exit code
  # which was present when the trap was initiated.
  # This would be the success/failure of the test.
  TEST_EXIT_CODE=${TEST_EXIT_CODE:-$?}

  # Disable logging of every command, as it is too verbose.
  set +x

  # If this is a gate node from OpenStack-Infra Store all logs into the
  #  execution directory after gate run.
  if [ "$GATE_EXIT_LOG_COPY" == true ]; then
    if [ "$GATE_EXIT_RUN_DSTAT" == true ]; then
      generate_dstat_charts || true
    fi

    # Disable logging of every command, as it is too verbose.
    # We have to do this here because log_instance_info does set -x
    set +x
  fi

  # System status & Information
  log_instance_info
}

function gate_log_requirements {
  # ensure packages are installed to get instance info
  determine_distro
  case ${DISTRO_ID} in
      ubuntu|debian)
          apt-get update
          DEBIAN_FRONTEND=noninteractive apt-get -y install iproute2 net-tools parallel
          ;;
      rocky|centos|rhel)
          dnf -y install epel-release
          sed -i 's/\[epel\]/&\nincludepkgs=parallel/' /etc/yum.repos.d/epel.repo
          dnf -y --enablerepo=epel install iproute parallel
          ;;
  esac
}

function setup_ara {
  # Install ARA and add it to the callback path provided by bootstrap-ansible.sh/openstack-ansible.rc
  # This is added *here* instead of bootstrap-ansible so it's used for CI purposes only.
  # PIP_COMMAND and PIP_OPTS are exported by the bootstrap-ansible script.
  # PIP_OPTS contains the whole set of constraints that need to be applied.
  ${PIP_COMMAND} install --isolated ${PIP_OPTS} "ara[server]"
}

function run_dstat {
  if [ "$GATE_EXIT_RUN_DSTAT" == true ]; then
    if [[ ! -d /opt/dool ]]; then
      git clone https://github.com/scottchiefbaker/dool /opt/dool
      python3 /opt/dool/install.py
    fi

    # https://stackoverflow.com/a/20338327 executing in ()& decouples the dstat
    # process from scripts-library to prevent hung builds if dstat fails to exit
    # for any reason.
    (dool -tcmsdn --top-cpu --top-mem --top-bio --nocolor --output /openstack/log/instance-info/dstat.csv \
        < /dev/null > /openstack/log/instance-info/dstat.log 2>&1 &)
  fi
}

function generate_dstat_charts {
  kill $(pgrep -f dool)
  if [[ ! -d /opt/dstat_graph ]]; then
    git clone https://opendev.org/opendev/dstat_graph /opt/dstat_graph
  fi
  pushd /opt/dstat_graph
    /usr/bin/env bash -e ./generate_page.sh /openstack/log/instance-info/dstat.csv > /openstack/log/instance-info/dstat.html
  popd
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
  # ensure packages are installed to get instance info
  determine_distro
  case ${DISTRO_ID} in
      ubuntu|debian)
          apt-get update
          DEBIAN_FRONTEND=noninteractive apt-get -y install iproute2 net-tools
          ;;
      rocky|centos|rhel)
          dnf -y install iproute
          ;;
  esac
  set +x
  # Get host information post initial setup and reset verbosity
  if [ ! -d "/openstack/log/instance-info" ];then
    mkdir -p "/openstack/log/instance-info"
  fi
  get_instance_info
  # Run log collection when needed
  if [ "${1:-false}" = "true" ]; then
    RUN_ARA="${GATE_EXIT_RUN_ARA}" WORKING_DIR="${GATE_LOG_DIR:-${HOME:-/opt}/osa-logs}" bash -e "$(dirname $(readlink -f ${BASH_SOURCE[0]}))/log-collect.sh"
  fi
  set -x
}

function get_repos_info {
  for i in /etc/apt/sources.list /etc/apt/sources.list.d/* /etc/yum.conf /etc/yum.repos.d/* /etc/zypp/repos.d/*; do
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
    command -v systemd-resolve &> /dev/null && \
      systemd-resolve --statistics && \
        cat /etc/systemd/resolved.conf) > \
          "/openstack/log/instance-info/host_dns_info_${TS}.log" || true
  if [ "$(command -v tracepath)" ]; then
    { tracepath "8.8.8.8" -m 5 2>/dev/null || tracepath "8.8.8.8"; } > \
      "/openstack/log/instance-info/host_tracepath_info_${TS}.log" || true
  fi
  if [ "$(command -v tracepath6)" ]; then
    { tracepath6 "2001:4860:4860::8888" -m 5 2>/dev/null || tracepath6 "2001:4860:4860::8888"; } >> \
      "/openstack/log/instance-info/host_tracepath_info_${TS}.log" || true
  fi
  if [ "$(command -v lxc-ls)" ]; then
    lxc-ls --fancy > \
      "/openstack/log/instance-info/host_lxc_container_info_${TS}.log" || true
  fi
  if [ "$(command -v lxc-checkconfig)" ]; then
    lxc-checkconfig > \
      "/openstack/log/instance-info/host_lxc_config_info_${TS}.log" || true
  fi
  if [ "$(command -v networkctl)" ]; then
    networkctl list > \
      "/openstack/log/instance-info/host_networkd_list_${TS}.log" || true
    networkctl status >> \
      "/openstack/log/instance-info/host_networkd_status_${TS}.log" || true
    networkctl lldp >> \
      "/openstack/log/instance-info/host_networkd_lldp_${TS}.log" || true
  fi
  if [ "$(command -v iptables)" ]; then
    (iptables -vnL && iptables -t nat -vnL && iptables -t mangle -vnL) > \
      "/openstack/log/instance-info/host_firewall_info_${TS}.log" || true
  fi
  if [ "$(command -v ansible)" ]; then
    ANSIBLE_HOST_KEY_CHECKING=False \
      ansible -i "localhost," localhost -m setup -c local > \
        "/openstack/log/instance-info/host_system_info_${TS}.log" || true
  fi
  get_repos_info > \
    "/openstack/log/instance-info/host_repo_info_${TS}.log" || true

  ip route get 1 > "/openstack/log/instance-info/routes_${TS}.log" || true
  ip link show > "/openstack/log/instance-info/links_${TS}.log" || true

  determine_distro
  case ${DISTRO_ID} in
      rocky|rhel)
          rpm -qa | sort > \
            "/openstack/log/instance-info/host_packages_info_${TS}.log" || true
          ;;
      ubuntu|debian)
          dpkg-query --list > \
            "/openstack/log/instance-info/host_packages_info_${TS}.log" || true
          ;;
  esac

  # Storage reports
  for dir_name in lxc machines; do
    if [ "$(command -v btrfs)" ]; then
      btrfs filesystem usage /var/lib/${dir_name} 2>/dev/null > \
        "/openstack/log/instance-info/btrfs_${dir_name}_usage_${TS}.log" || true
      btrfs filesystem show /var/lib/${dir_name} 2>/dev/null > \
        "/openstack/log/instance-info/btrfs_${dir_name}_show_${TS}.log" || true
      btrfs filesystem df /var/lib/${dir_name} 2>/dev/null > \
        "/openstack/log/instance-info/btrfs_${dir_name}_df_${TS}.log" || true
      btrfs qgroup show --human-readable -pcre --iec /var/lib/${dir_name} 2>/dev/null > \
        "/openstack/log/instance-info/btrfs_${dir_name}_quotas_${TS}.log" || true
    fi
  done

  if [ "$(command -v zfs)" ]; then
    zfs list > "/openstack/log/instance-info/zfs_lxc_${TS}.log" || true
  fi

  df -h > "/openstack/log/instance-info/report_fs_df_${TS}.log" || true
  lsmod > "/openstack/log/instance-info/lsmod_${TS}.log" || true
  free -m > "/openstack/log/instance-info/free_${TS}.log" || true
  cat /proc/cpuinfo > "/openstack/log/instance-info/cpuinfo_${TS}.log" || true
  ps -eo user,pid,ppid,lwp,%cpu,%mem,size,rss,cmd > "/openstack/log/instance-info/ps_${TS}.log" || true

  # Check if system has netstat or iproute2
  if command -v ss >/dev/null; then
    ss -tulpn > "/openstack/log/instance-info/ss_${TS}.log" || true
  fi
  if command -v netstat >/dev/null; then
    netstat -tulpn > "/openstack/log/instance-info/netstat_${TS}.log" || true
  fi
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
