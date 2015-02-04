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


## Shell Opts ----------------------------------------------------------------
set -e -u -v +x

## Vars
DEPLOY_SWIFT=${DEPLOY_SWIFT:-"yes"}
FLUSH_IPTABLES=${FLUSH_IPTABLES:-"yes"}

## Functions -----------------------------------------------------------------

info_block "Checking for required libraries." || source $(dirname ${0})/scripts-library.sh

## Main ----------------------------------------------------------------------

# Enable logging of all commands executed
set -x

# update the package cache and install required packages
apt-get update && apt-get install -y \
                   python-dev \
                   python2.7 \
                   build-essential \
                   curl \
                   git-core \
                   ipython \
                   tmux \
                   vim \
                   vlan \
                   bridge-utils \
                   lvm2 \
                   xfsprogs \
                   linux-image-extra-$(uname -r)

# output diagnostic information
get_instance_info && set -x

if [ "${FLUSH_IPTABLES}" == "yes" ]; then
  # Flush all the iptables rules set by openstack-infra
  iptables -F
  iptables -X
  iptables -t nat -F
  iptables -t nat -X
  iptables -t mangle -F
  iptables -t mangle -X
  iptables -P INPUT ACCEPT
  iptables -P FORWARD ACCEPT
  iptables -P OUTPUT ACCEPT
fi

# Ensure newline at end of file (missing on Rackspace public cloud Trusty image)
if ! cat -E /etc/ssh/sshd_config | tail -1 | grep -q "\$$"; then
  echo >> /etc/ssh/sshd_config
fi

# Ensure that sshd permits root login, or ansible won't be able to connect
if grep -q "^PermitRootLogin" /etc/ssh/sshd_config; then
  sed -i 's/^PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
else
  echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
fi

# create /opt if it doesn't already exist
if [ ! -d "/opt" ];then
  mkdir /opt
fi

# create /etc/rc.local if it doesn't already exist
if [ ! -f "/etc/rc.local" ];then
  touch /etc/rc.local
  chmod +x /etc/rc.local
fi

# ensure that the ssh key exists and is an authorized_key
ssh_key_create

# prepare the storage appropriately
configure_diskspace

# build the loopback drive for swap to use
loopback_create /opt/swap.img 1024M thick swap

# Ensure swap will be used on the host
sysctl -w vm.swappiness=10 | tee -a /etc/sysctl.conf

# build the loopback drive for cinder to use
# but only if the cinder-volumes vg doesn't already exist
if ! vgs cinder-volumes > /dev/null 2>&1; then
  CINDER="cinder.img"
  loopback_create /opt/${CINDER} 10G thin rc
  CINDER_DEVICE=$(losetup -a | awk -F: "/${CINDER}/ {print \$1}")
  pvcreate ${CINDER_DEVICE}
  pvscan
  vgcreate cinder-volumes ${CINDER_DEVICE}
fi

# build the loopback drives for swift to use
if [ "${DEPLOY_SWIFT}" == "yes" ]; then
  for SWIFT in swift1.img swift2.img swift3.img; do
    loopback_create /opt/${SWIFT} 10G thin none
    if ! grep -q "^/opt/${SWIFT}" /etc/fstab; then
      echo "/opt/${SWIFT} /srv/${SWIFT} xfs loop,noatime,nodiratime,nobarrier,logbufs=8 0 0" >> /etc/fstab
    fi
    if ! mount | grep -q "^/opt/${SWIFT}"; then
      mkfs.xfs -f /opt/${SWIFT}
      mkdir -p /srv/${SWIFT}
      mount /srv/${SWIFT}
    fi
  done
fi

# copy the required interfaces configuration file into place
IFACE_CFG_SOURCE="etc/network/interfaces.d/aio_interfaces.cfg"
IFACE_CFG_TARGET="/${IFACE_CFG_SOURCE}"
cp ${IFACE_CFG_SOURCE} ${IFACE_CFG_TARGET}

# Ensure the network source is in place
if ! grep -q "^source /etc/network/interfaces.d/\*.cfg$" /etc/network/interfaces; then
  echo -e "\nsource /etc/network/interfaces.d/*.cfg" | tee -a /etc/network/interfaces
fi

# Set base DNS to google, ensuring consistent DNS in different environments
echo -e 'nameserver 8.8.8.8\nnameserver 8.8.4.4' | tee /etc/resolv.conf

# Bring up the new interfaces
for iface in $(awk '/^iface/ {print $2}' ${IFACE_CFG_TARGET}); do
  /sbin/ifup $iface || true
done

# output an updated set of diagnostic information
get_instance_info

# Final message
info_block "The system has been prepared for an all-in-one build."
