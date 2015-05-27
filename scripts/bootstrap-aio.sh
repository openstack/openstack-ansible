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
export FLUSH_IPTABLES=${FLUSH_IPTABLES:-"yes"}

# Ubuntu repos
UBUNTU_RELEASE=$(lsb_release -sc)
UBUNTU_REPO=${UBUNTU_REPO:-"http://mirror.rackspace.com/ubuntu"}
UBUNTU_SEC_REPO=${UBUNTU_SEC_REPO:-"http://mirror.rackspace.com/ubuntu"}


## Functions -----------------------------------------------------------------

info_block "Checking for required libraries." || source $(dirname ${0})/scripts-library.sh

## Main ----------------------------------------------------------------------

# Make the /openstack/log directory for openstack-infra gate check log publishing
mkdir -p /openstack/log

# Implement the log directory link for openstack-infra log publishing
ln -sf /openstack/log $SYMLINK_DIR

# Create ansible logging directory and add in a log file entry into ansible.cfg
if [ -f "rpc_deployment/ansible.cfg" ];then
  mkdir -p /openstack/log/ansible-logging
  if [ ! "$(grep -e '^log_path\ =\ /openstack/log/ansible-logging/ansible.log' rpc_deployment/ansible.cfg)" ];then
    sed -i '/\[defaults\]/a log_path = /openstack/log/ansible-logging/ansible.log' rpc_deployment/ansible.cfg
  fi
fi

# Check that the link creation was successful
[[ -d $SYMLINK_DIR ]] || exit_fail
if ! [ -d $SYMLINK_DIR ] ; then
    echo "Could not create a link from /openstack/log to ${SYMLINK_DIR}"
    exit_fail
fi

# Enable logging of all commands executed
set -x

# Update the package cache
apt-get update

# Remove known conflicting packages in the base image
apt-get purge -y libmysqlclient18 mysql-common

# Install required packages
apt-get install -y python-dev \
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
log_instance_info && set -x

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

# copy the required interfaces configuration file into place
IFACE_CFG_SOURCE="etc/network/interfaces.d/aio_interfaces.cfg"
IFACE_CFG_TARGET="/${IFACE_CFG_SOURCE}"
cp ${IFACE_CFG_SOURCE} ${IFACE_CFG_TARGET}

# Ensure the network source is in place
if ! grep -q "^source /etc/network/interfaces.d/\*.cfg$" /etc/network/interfaces; then
  echo -e "\nsource /etc/network/interfaces.d/*.cfg" | tee -a /etc/network/interfaces
fi


# Set base DNS to google, ensuring consistent DNS in different environments
if [ ! "$(grep -e '^nameserver 8.8.8.8' -e '^nameserver 8.8.4.4' /etc/resolv.conf)" ];then
  echo -e '\n# Adding google name servers\nnameserver 8.8.8.8\nnameserver 8.8.4.4' | tee -a /etc/resolv.conf
fi

# Set the host repositories to only use the same ones, always, for the sake of consistency.
cat > /etc/apt/sources.list <<EOF
# Normal repositories
deb ${UBUNTU_REPO} ${UBUNTU_RELEASE} main restricted
deb ${UBUNTU_REPO} ${UBUNTU_RELEASE}-updates main restricted
deb ${UBUNTU_REPO} ${UBUNTU_RELEASE} universe
deb ${UBUNTU_REPO} ${UBUNTU_RELEASE}-updates universe
deb ${UBUNTU_REPO} ${UBUNTU_RELEASE} multiverse
deb ${UBUNTU_REPO} ${UBUNTU_RELEASE}-updates multiverse
# Backports repositories
deb ${UBUNTU_REPO} ${UBUNTU_RELEASE}-backports main restricted universe multiverse
# Security repositories
deb ${UBUNTU_SEC_REPO} ${UBUNTU_RELEASE}-security main restricted
deb ${UBUNTU_SEC_REPO} ${UBUNTU_RELEASE}-security universe
deb ${UBUNTU_SEC_REPO} ${UBUNTU_RELEASE}-security multiverse
EOF

# Bring up the new interfaces
for iface in $(awk '/^iface/ {print $2}' ${IFACE_CFG_TARGET}); do
  /sbin/ifup $iface || true
done

# output an updated set of diagnostic information
log_instance_info

# Final message
info_block "The system has been prepared for an all-in-one build."
