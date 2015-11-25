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
BOOTSTRAP_AIO_DIR=${BOOTSTRAP_AIO_DIR:-"/openstack"}
DATA_DISK_DEVICE=${DATA_DISK_DEVICE:-}
MIN_DISK_SIZE_GB=${MIN_DISK_SIZE_GB:-80}
REPORT_DATA=${REPORT_DATA:-""}
ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-""}
STARTTIME="${STARTTIME:-$(date +%s)}"

# The default SSHD configuration has MaxSessions = 10. If a deployer changes
#  their SSHD config, then the FORKS may be set to a higher number. We set the
#  value to 10 or the number of CPU's, whichever is less. This is to balance
#  between performance gains from the higher number, and CPU consumption. If
#  FORKS is already set to a value, then we leave it alone.
if [ -z "${FORKS:-}" ]; then
  CPU_NUM=$(grep -c ^processor /proc/cpuinfo)
  if [ ${CPU_NUM} -lt "10" ]; then
    FORKS=${CPU_NUM}
  else
    FORKS=10
  fi
fi


## Functions -----------------------------------------------------------------
# Used to retry a process that may fail due to random issues.
function successerator {
  set +e
  # Get the time that the method was started.
  OP_START_TIME=$(date +%s)
  RETRY=0
  # Set the initial return value to failure.
  false
  while [ $? -ne 0 -a ${RETRY} -lt ${MAX_RETRIES} ];do
    ((RETRY++))
    if [ ${RETRY} -gt 1 ];then
      $@ -vvvv
    else
      $@
    fi
  done
  # If max retires were hit, fail.
  if [ $? -ne 0 ] && [ ${RETRY} -eq ${MAX_RETRIES} ];then
    echo -e "\nHit maximum number of retries, giving up...\n"
    exit_fail
  fi
  # Print the time that the method completed.
  OP_TOTAL_SECONDS="$(( $(date +%s) - OP_START_TIME ))"
  REPORT_OUTPUT="${OP_TOTAL_SECONDS} seconds"
  REPORT_DATA+="- Operation: [ $@ ]\t${REPORT_OUTPUT}\tNumber of Attempts [ ${RETRY} ]\n"
  echo -e "Run Time = ${REPORT_OUTPUT}"
  set -e
}

function install_bits {
  # Use the successerator to run openstack-ansible with
  # the appropriate number of forks
  successerator openstack-ansible ${ANSIBLE_PARAMETERS} --forks ${FORKS} $@
}

function configure_diskspace {
  # If there are any block devices available other than the one
  # used for the root disk, repurpose it for our needs.

  # If DATA_DISK_DEVICE is not set or empty, then try to figure out which
  #  device to use
  if [ -z "${DATA_DISK_DEVICE}" ]; then
    # Identify the list of disk devices available, sort from largest to
    #  smallest, and pick the largest.
    # Excludes:
    #   - the first device, as that is where the OS is expected
    #   - read only devices, as we can't write to them
    DATA_DISK_DEVICE=$(lsblk -brndo NAME,TYPE,RO,SIZE | \
                       awk '/d[b-z]+ disk 0/{ if ($4>m){m=$4; d=$1}}; END{print d}')
  fi

  # We only want to continue if a device was found to use. If not,
  #  then we simply leave the disks alone.
  if [ ! -z "${DATA_DISK_DEVICE}" ]; then
    # Calculate the minimum disk size in bytes
    MIN_DISK_SIZE_B=$((MIN_DISK_SIZE_GB * 1024 * 1024 * 1024))

    # Determine the size in bytes of the selected device
    blk_dev_size_b=$(lsblk -nrdbo NAME,TYPE,SIZE | \
                     awk "/^${DATA_DISK_DEVICE} disk/ {print \$3}")

    # Determine if the device is large enough
    if [ "${blk_dev_size_b}" -ge "${MIN_DISK_SIZE_B}" ]; then
      # Only execute the disk partitioning process if a partition labeled
      #  'openstack-data{1,2}' is not present and that partition is not
      #  formatted as ext4. This is an attempt to achieve idempotency just
      #  in case this script is run multiple times.
      if ! parted --script -l -m | egrep -q ':ext4:openstack-data[12]:;$'; then

        # Dismount any mount points on the device
        mount_points=$(awk "/^\/dev\/${DATA_DISK_DEVICE}[0-9]* / {print \$2}" /proc/mounts)
        for mount_point in ${mount_points}; do
          umount ${mount_point}
          sed -i ":${mount_point}:d" /etc/fstab
        done

        # Partition the whole disk for our usage
        parted --script /dev/${DATA_DISK_DEVICE} mklabel gpt
        parted --align optimal --script /dev/${DATA_DISK_DEVICE} mkpart openstack-data1 ext4 0% 40%
        parted --align optimal --script /dev/${DATA_DISK_DEVICE} mkpart openstack-data2 ext4 40% 100%

        # Format the bootstrap partition, create the mount point, and mount it.
        mkfs.ext4 /dev/${DATA_DISK_DEVICE}1
        mkdir -p ${BOOTSTRAP_AIO_DIR}
        mount /dev/${DATA_DISK_DEVICE}1 ${BOOTSTRAP_AIO_DIR}

        # Format the lxc partition, create the mount point, and mount it.
        mkfs.ext4 /dev/${DATA_DISK_DEVICE}2
        mkdir -p /var/lib/lxc
        mount /dev/${DATA_DISK_DEVICE}2 /var/lib/lxc

      fi
      # Add the fstab entries if they aren't there already
      if ! grep -qw "^/dev/${DATA_DISK_DEVICE}1" /etc/fstab; then
        echo "/dev/${DATA_DISK_DEVICE}1 ${BOOTSTRAP_AIO_DIR} ext4 defaults 0 0" >> /etc/fstab
      fi
      if ! grep -qw "^/dev/${DATA_DISK_DEVICE}2" /etc/fstab; then
        echo "/dev/${DATA_DISK_DEVICE}2 /var/lib/lxc ext4 defaults 0 0" >> /etc/fstab
      fi
    fi
  fi
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
  if [ ! -f "${key_file}" -a ! -f "${key_file}.pub" ]; then
    rm -f ${key_file}*
    ssh-keygen -t rsa -f ${key_file} -N ''
  fi

  # Ensure that the public key is included in the authorized_keys
  # for the default root directory and the current home directory
  key_content=$(cat "${key_file}.pub")
  if ! grep -q "${key_content}" ${key_path}/authorized_keys; then
    echo "${key_content}" | tee -a ${key_path}/authorized_keys
  fi
}

function loopback_create {
  LOOP_FILENAME=${1}
  LOOP_FILESIZE=${2}
  LOOP_FILE_TYPE=${3}  # thin, thick
  LOOP_MOUNT_METHOD=${4}  # swap, rc, none

  if [ ! -f "${LOOP_FILENAME}" ]; then
    if [ "${LOOP_FILE_TYPE}" = "thin" ]; then
      truncate -s ${LOOP_FILESIZE} ${LOOP_FILENAME}
    elif [ "${LOOP_FILE_TYPE}" = "thick" ]; then
      fallocate -l ${LOOP_FILESIZE} ${LOOP_FILENAME} &> /dev/null || \
      dd if=/dev/zero of=${LOOP_FILENAME} bs=1M count=$(( LOOP_FILESIZE / 1024 / 1024 ))
    else
      exit_fail "No valid option ${LOOP_FILE_TYPE} found."
    fi
  fi

  if [ "${LOOP_MOUNT_METHOD}" = "rc" ]; then
    if ! losetup -a | grep -q "(${LOOP_FILENAME})$"; then
      LOOP_DEVICE=$(losetup -f)
      losetup ${LOOP_DEVICE} ${LOOP_FILENAME}
    fi
    if ! grep -q ${LOOP_FILENAME} /etc/rc.local; then
      sed -i "\$i losetup \$(losetup -f) ${LOOP_FILENAME}" /etc/rc.local
    fi
  fi

  if [ "${LOOP_MOUNT_METHOD}" = "swap" ]; then
    if ! swapon -s | grep -q ${LOOP_FILENAME}; then
      mkswap ${LOOP_FILENAME}
      swapon -a
    fi
    if ! grep -q "^${LOOP_FILENAME} " /etc/fstab; then
      echo "${LOOP_FILENAME} none swap loop 0 0" >> /etc/fstab
    fi
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
  get_instance_info &> /openstack/log/instance-info/host_info_$(date +%s).log
  set -x
}

function get_repos_info {
  for i in /etc/apt/sources.list /etc/apt/sources.list.d/*; do
    echo -e "\n$i"
    cat $i
  done
}

# Get instance info
function get_instance_info {
  set +x
  info_block 'Current User'
  whoami
  info_block 'Available Memory'
  free -mt || true
  info_block 'Available Disk Space'
  df -h || true
  info_block 'Mounted Devices'
  mount || true
  info_block 'Block Devices'
  lsblk -i || true
  info_block 'Block Devices Information'
  blkid || true
  info_block 'Block Device Partitions'
  for i in /dev/xv* /dev/sd* /dev/vd*; do
    if [ -b "$i" ];then
      parted --script $i print || true
    fi
  done
  info_block 'PV Information'
  pvs || true
  info_block 'VG Information'
  vgs || true
  info_block 'LV Information'
  lvs || true
  info_block 'CPU Information'
  which lscpu && lscpu || true
  info_block 'Kernel Information'
  uname -a || true
  info_block 'Container Information'
  which lxc-ls && lxc-ls --fancy || true
  info_block 'Firewall Information'
  iptables -vnL || true
  iptables -t nat -vnL || true
  iptables -t mangle -vnL || true
  info_block 'Network Devices'
  ip a || true
  info_block 'Network Routes'
  ip r || true
  info_block 'DNS Configuration'
  cat /etc/resolv.conf
  info_block 'Trace Path from google'
  tracepath 8.8.8.8 -m 5 || true
  info_block 'XEN Server Information'
  if (which xenstore-read);then
    xenstore-read vm-data/provider_data/provider || echo "\nxenstore Read Failed - Skipping\n"
  else
    echo -e "\nNo xenstore Information\n"
  fi
  get_repos_info &> /openstack/log/instance-info/host_repo_info_$(date +%s).log || true
  dpkg-query --list &> /openstack/log/instance-info/host_packages_info_$(date +%s).log
}

function print_report {
  # Print the stored report data
  echo -e "${REPORT_DATA}"
}

function get_pip {
  # if pip is already installed, don't bother doing anything
  if [ ! "$(which pip)" ]; then

    # If GET_PIP_URL is set, then just use it
    if [ -n "${GET_PIP_URL:-}" ]; then
      curl --silent ${GET_PIP_URL} > /opt/get-pip.py
      if head -n 1 /opt/get-pip.py | grep python; then
        python2 /opt/get-pip.py || python /opt/get-pip.py
        return
      fi
    fi

    # Try getting pip from bootstrap.pypa.io as a primary source
    curl --silent https://bootstrap.pypa.io/get-pip.py > /opt/get-pip.py
    if head -n 1 /opt/get-pip.py | grep python; then
      python2 /opt/get-pip.py || python /opt/get-pip.py
      return
    fi

    # Try the get-pip.py from the github repository as a secondary source
    curl --silent https://raw.github.com/pypa/pip/master/contrib/get-pip.py > /opt/get-pip.py
    if head -n 1 /opt/get-pip.py | grep python; then
      python2 /opt/get-pip.py || python /opt/get-pip.py
      return
    fi

    echo "A suitable download location for get-pip.py could not be found."
    exit_fail
  fi
}


## Signal traps --------------------------------------------------------------
# Trap all Death Signals and Errors
trap "exit_fail ${LINENO} $? 'Received STOP Signal'" SIGHUP SIGINT SIGTERM
trap "exit_fail ${LINENO} $?" ERR

## Determine OS --------------------------------------------------------------
# Determine the operating system of the base host
# Adds the $HOST_DISTRO, $HOST_VERSION, and $HOST_CODENAME bash variables.
eval "$(python $(dirname ${BASH_SOURCE})/os-detection.py)"
echo "Detected ${HOST_DISTRO} ${HOST_VERSION} (codename: ${HOST_CODENAME})"

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
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Export the home directory just in case it's not set
export HOME="/root"
