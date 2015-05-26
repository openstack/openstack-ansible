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
MIN_LXC_VG_SIZE_GB=${MIN_LXC_VG_SIZE_GB:-250}
REPORT_DATA=${REPORT_DATA:-""}
FORKS=${FORKS:-25}
ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-""}
STARTTIME="${STARTTIME:-$(date +%s)}"


## Functions -----------------------------------------------------------------
# Used to retry a process that may fail due to random issues.
function successerator() {
  set +e
  # Get the time that the method was started.
  OP_START_TIME="$(date +%s)"
  RETRY=0
  # Set the initial return value to failure.
  false
  while [ $? -ne 0 -a ${RETRY} -lt ${MAX_RETRIES} ];do
    RETRY=$((${RETRY}+1))
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
  OP_TOTAL_SECONDS="$[$(date +%s) - $OP_START_TIME]"
  REPORT_OUTPUT="${OP_TOTAL_SECONDS} seconds"
  REPORT_DATA+="- Operation: [ $@ ]\t${REPORT_OUTPUT}\tNumber of Attempts [ ${RETRY} ]\n"
  echo -e "Run Time = ${REPORT_OUTPUT}"
  set -e
}

function install_bits() {
  # The number of forks has been limited to 10 by default (2x ansible default)
  # This will also run ansible in 3x verbose mode
  successerator openstack-ansible ${ANSIBLE_PARAMETERS} --forks ${FORKS} $@
}

function configure_diskspace() {
  # If there are any block devices available other than the one
  # used for the root disk, repurpose it for our needs.
  MIN_LXC_VG_SIZE_B=$((${MIN_LXC_VG_SIZE_GB} * 1024 * 1024 * 1024))

  # only do this if the lxc vg doesn't already exist
  if ! vgs lxc > /dev/null 2>&1; then
    blk_devices=$(lsblk -nrdo NAME,TYPE | awk '/d[b-z]+ disk/ {print $1}')
    for blk_dev in ${blk_devices}; do
      # dismount any mount points on the device
      mount_points=$(awk "/^\/dev\/${blk_dev}[0-9]* / {print \$2}" /proc/mounts)
      for mount_point in ${mount_points}; do
        umount ${mount_point}
        sed -i ":${mount_point}:d" /etc/fstab
      done

      # add a vg for lxc
      blk_dev_size_b=$(lsblk -nrdbo NAME,TYPE,SIZE | awk "/^${blk_dev} disk/ {print \$3}")
      if [ "${blk_dev_size_b}" -gt "${MIN_LXC_VG_SIZE_B}" ]; then
        if ! vgs lxc > /dev/null 2>&1; then
          parted --script /dev/${blk_dev} mklabel gpt
          parted --align optimal --script /dev/${blk_dev} mkpart lxc 0% 80%
          part_num=$(parted /dev/${blk_dev} print --machine | awk -F':' '/lxc/ {print $1}')
          pvcreate -ff -y /dev/${blk_dev}${part_num}
          vgcreate lxc /dev/${blk_dev}${part_num}
        fi
        # add a vg for cinder volumes, but only if it doesn't already exist
        if ! vgs cinder-volumes > /dev/null 2>&1; then
          parted --align optimal --script /dev/${blk_dev} mkpart cinder 80% 100%
          part_num=$(parted /dev/${blk_dev} print --machine | awk -F':' '/cinder/ {print $1}')
          pvcreate -ff -y /dev/${blk_dev}${part_num}
          vgcreate cinder-volumes /dev/${blk_dev}${part_num}
        fi
      else
        if ! grep '/var/lib/lxc' /proc/mounts 2>&1; then
          parted --script /dev/${blk_dev} mklabel gpt
          parted --script /dev/${blk_dev} mkpart lxc ext4 0% 100%
          part_num=$(parted /dev/${blk_dev} print --machine | awk -F':' '/lxc/ {print $1}')
          # Format, Create, and Mount it all up.
          mkfs.ext4 /dev/${blk_dev}${part_num}
          mkdir -p /var/lib/lxc
          mount /dev/${blk_dev}${part_num} /var/lib/lxc
        fi
      fi
    done
  fi
}

function ssh_key_create() {
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

function loopback_create() {
  LOOP_FILENAME=${1}
  LOOP_FILESIZE=${2}
  LOOP_FILE_TYPE=${3}  # thin, thick
  LOOP_MOUNT_METHOD=${4}  # swap, rc, none

  if [ ! -f "${LOOP_FILENAME}" ]; then
    if [ "${LOOP_FILE_TYPE}" = "thin" ]; then
      truncate -s ${LOOP_FILESIZE} ${LOOP_FILENAME}
    elif [ "${LOOP_FILE_TYPE}" = "thick" ]; then
      fallocate -l ${LOOP_FILESIZE} ${LOOP_FILENAME} &> /dev/null || \
      dd if=/dev/zero of=${LOOP_FILENAME} bs=1M count=$(( ${LOOP_FILESIZE} / 1024 / 1024 ))
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

function exit_state() {
  set +x
  TOTALSECONDS="$[$(date +%s) - $STARTTIME]"
  info_block "Run Time = ${TOTALSECONDS} seconds || $(($TOTALSECONDS / 60)) minutes"
  if [ "${1}" == 0 ];then
    info_block "Status: Success"
  else
    info_block "Status: Failure"
  fi
  exit ${1}
}

function exit_success() {
  set +x
  exit_state 0
}

function exit_fail() {
  set +x
  log_instance_info
  info_block "Error Info - $@"
  exit_state 1
}

function print_info() {
  PROC_NAME="- [ $@ ] -"
  printf "\n%s%s\n" "$PROC_NAME" "${LINE:${#PROC_NAME}}"
}

function info_block(){
  echo "${LINE}"
  print_info "$@"
  echo "${LINE}"
}

function log_instance_info() {
  set +x
  # Get host information post initial setup and reset verbosity
  if [ ! -d "/openstack/log/instance-info" ];then
    mkdir -p "/openstack/log/instance-info"
  fi
  get_instance_info &> /openstack/log/instance-info/host_info_$(date +%s).log
  set -x
}

function get_repos_info() {
  for i in /etc/apt/sources.list /etc/apt/sources.list.d/*; do
    echo -e "\n$i"
    cat $i
  done
}

# Get instance info
function get_instance_info() {
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

function print_report() {
  # Print the stored report data
  echo -e "${REPORT_DATA}"
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
  echo -e "Example: /opt/os-ansible-deployment/\n"
  exit_state 1
fi


## Exports -------------------------------------------------------------------
# Export known paths
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Export the home directory just in case it's not set
export HOME="/root"
