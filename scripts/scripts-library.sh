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

## Variables -----------------------------------------------------------------
LINE='-----------------------------------------------------------------------'
STARTTIME=${STARTTIME:-"$(date +%s)"}
REPORT_DATA=""
MAX_RETRIES=${MAX_RETRIES:-0}

# Export known paths
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Override the current HOME directory
export HOME="/root"

## Functions -----------------------------------------------------------------

# Output details provided as parameters
function print_info() {
  set +x
  PROC_NAME="- [ $@ ] -"
  printf "\n%s%s\n" "$PROC_NAME" "${LINE:${#PROC_NAME}}"
}

# Output a formatted block around a message
function info_block(){
  set +x
  echo "${LINE}"
  print_info "$@"
  echo "${LINE}"
}

# Output a formatted block of information about the run on exit
function exit_state() {
  set +x
  info_block "Run time reports"
  echo -e "${REPORT_DATA}"
  TOTALSECONDS="$[$(date +%s) - $STARTTIME]"
  info_block "Run Time = ${TOTALSECONDS} seconds || $(($TOTALSECONDS / 60)) minutes"
  if [ "${1}" == 0 ];then
    info_block "Status: Build Success"
  else
    info_block "Status: Build Failure"
  fi
  exit ${1}
}

# Exit with error details
function exit_fail() {
  set +x
  get_instance_info
  info_block "Error Info - $@"
  exit_state 1
}

# Output diagnostic information
function get_instance_info() {
  set +x
  info_block 'Path'
  echo ${PATH}
  info_block 'Current User'
  whoami
  info_block 'Home Directory'
  echo ${HOME}
  info_block 'Available Memory'
  free -mt
  info_block 'Available Disk Space'
  df -h
  info_block 'Mounted Devices'
  mount
  info_block 'Block Devices'
  lsblk -i
  info_block 'Block Devices Information'
  blkid
  info_block 'Block Device Partitions'
  for blk_dev in $(lsblk -nrdo NAME,TYPE | awk '/disk/ {print $1}'); do
    # Ignoring errors for the below command is important as sometimes
    # the block device in question is unpartitioned or has an invalid
    # partition. In this case, parted returns 'unrecognised disk label'
    # and the bash script exits due to the -e environment setting.
    parted /dev/$blk_dev print || true
  done
  info_block 'PV Information'
  pvs
  info_block 'VG Information'
  vgs
  info_block 'LV Information'
  lvs
  info_block 'Contents of /etc/fstab'
  cat /etc/fstab
  info_block 'CPU Information'
  which lscpu && lscpu
  info_block 'Kernel Information'
  uname -a
  info_block 'Container Information'
  which lxc-ls && lxc-ls --fancy
  info_block 'Firewall Information'
  iptables -vnL
  iptables -t nat -vnL
  iptables -t mangle -vnL
  info_block 'Network Devices'
  ip a
  info_block 'Network Routes'
  ip r
  info_block 'Trace Path from google'
  tracepath 8.8.8.8 -m 5
  info_block 'XEN Server Information'
  which xenstore-read && xenstore-read vm-data/provider_data/provider ||:
}

# Used to retry a process that may fail due to transient issues
function successerator() {
  set +e +x
  # Get the time that the method was started.
  OP_START_TIME="$(date +%s)"
  MAX_ATTEMPTS=$((${MAX_RETRIES}+1))

  for ATTEMPT in $(seq ${MAX_ATTEMPTS}); do
    $@ && { report_success; return 0; }
  done

  exit_fail "Hit maximum number of retries, giving up..."
  set -e -x
}

# Report success
function report_success() {
  OP_TOTAL_SECONDS="$[$(date +%s) - $OP_START_TIME]"
  REPORT_OUTPUT="${OP_TOTAL_SECONDS} seconds"
  REPORT_DATA+="- Operation: [ $@ ]\t${REPORT_OUTPUT}\tNumber of Attempts [ ${ATTEMPT} ]\n"
  print_info "Run Time = ${REPORT_OUTPUT}"
}

function ssh_key_create(){
  # Ensure that the ssh key exists and is an authorized_key
  key_path="${HOME}/.ssh"
  key_file="${key_path}/id_rsa"

  # Ensure that the .ssh directory exists and has the right mode
  if [ ! -d ${key_path} ]; then
    mkdir -p ${key_path}
    chmod 700 ${key_path}
  fi
  if [ ! -f "${key_file}" ] || [ ! -f "${key_file}.pub" ]; then
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

function configure_diskspace(){
  # If there are any block devices available other than the one
  # used for the root disk, repurpose it for our needs.

  # the disk we use needs to have at least 60GB of space
  min_disk_size_b=$((60 * 1024 * 1024 * 1024))

  blk_devices=$(lsblk -nrdo NAME,TYPE | awk '/d[b-z]+ disk/ {print $1}')
  for blk_dev in ${blk_devices}; do
    # only do this if the cinder-volumes vg doesn't already exist
    if ! vgs cinder-volumes > /dev/null 2>&1; then

      blk_dev_size_b=$(lsblk -nrdbo NAME,TYPE,SIZE | awk "/^${blk_dev} disk/ {print \$3}")
      if [ "${blk_dev_size_b}" -gt "${min_disk_size_b}" ]; then
        # dismount any mount points on the device
        mount_points=$(awk "/^\/dev\/${blk_dev}[0-9]* / {print \$2}" /proc/mounts)
        for mount_point in ${mount_points}; do
          umount ${mount_point}
        done

        #add a vg for cinder volumes
        parted --script /dev/${blk_dev} mklabel gpt
        parted --align optimal --script /dev/${blk_dev} mkpart cinder 0% 100%
        pvcreate -ff -y /dev/${blk_dev}1
        vgcreate cinder-volumes /dev/${blk_dev}1

        # add an lv for lxc to use
        # it does not use it's own vg to ensure that the container disk usage
        # is thin-provisioned in the simplest way as openstack-infra instances
        # do not have enough disk space to handle thick-provisioned containers
        lvcreate -n lxc -L50g cinder-volumes

        # prepare the file system and mount it
        mkfs.ext4 /dev/cinder-volumes/lxc
        mkdir -p /var/lib/lxc
        mount /dev/cinder-volumes/lxc /var/lib/lxc
      fi

    fi
  done
}

function loopback_create() {
  LOOP_FILENAME=${1}
  LOOP_FILESIZE=${2}
  LOOP_FILE_TYPE=${3}    # thin, thick
  LOOP_MOUNT_METHOD=${4} # swap, rc, none

  if [ ! -f "${LOOP_FILENAME}" ]; then
    if [ "${LOOP_FILE_TYPE}" = "thin" ]; then
      truncate -s ${LOOP_FILESIZE} ${LOOP_FILENAME}
    elif [ "${LOOP_FILE_TYPE}" = "thick" ]; then
      dd if=/dev/zero of=${LOOP_FILENAME} bs=${LOOP_FILESIZE} count=1
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

# Exit if the script is not being run as root
if [ ! "$(whoami)" == "root" ]; then
  info_block "This script must be run as root."
  exit 1
fi

# Check that we are in the root path of the cloned repo
if [ ! -d "etc" -a ! -d "scripts" -a ! -f "requirements.txt" ]; then
  info_block "ERROR: Please execute this script from the root directory of the cloned source code."
  exit 1
fi

# Trap all Death Signals and Errors
trap "exit_fail ${LINENO} $? 'Received STOP Signal'" SIGHUP SIGINT SIGTERM
trap "exit_fail ${LINENO} $?" ERR
