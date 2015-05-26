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
set -e -u -x


## Vars ----------------------------------------------------------------------
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-"secrete"}
export SERVICE_REGION=${SERVICE_REGION:-"RegionOne"}
export DEPLOY_SWIFT=${DEPLOY_SWIFT:-"yes"}
export GET_PIP_URL=${GET_PIP_URL:-"https://bootstrap.pypa.io/get-pip.py"}
export PUBLIC_INTERFACE=${PUBLIC_INTERFACE:-$(ip route show | awk '/default/ { print $NF }')}
export PUBLIC_ADDRESS=${PUBLIC_ADDRESS:-$(ip -o -4 addr show dev ${PUBLIC_INTERFACE} | awk -F '[ /]+' '/global/ {print $4}')}
export NOVA_VIRT_TYPE=${NOVA_VIRT_TYPE:-"qemu"}
export TEMPEST_FLAT_CIDR=${TEMPEST_FLAT_CIDR:-"172.29.248.0/22"}
export FLUSH_IPTABLES=${FLUSH_IPTABLES:-"yes"}
export RABBITMQ_PACKAGE_URL=${RABBITMQ_PACKAGE_URL:-""}
export SYMLINK_DIR=${SYMLINK_DIR:-"$(pwd)/logs"}

# Default disabled fatal deprecation warnings
export CINDER_FATAL_DEPRECATIONS=${CINDER_FATAL_DEPRECATIONS:-"no"}
export GLANCE_FATAL_DEPRECATIONS=${GLANCE_FATAL_DEPRECATIONS:-"no"}
export HEAT_FATAL_DEPRECATIONS=${HEAT_FATAL_DEPRECATIONS:-"no"}
export KEYSTONE_FATAL_DEPRECATIONS=${KEYSTONE_FATAL_DEPRECATIONS:-"no"}
export NEUTRON_FATAL_DEPRECATIONS=${NEUTRON_FATAL_DEPRECATIONS:-"no"}
export NOVA_FATAL_DEPRECATIONS=${NOVA_FATAL_DEPRECATIONS:-"no"}
export TEMPEST_FATAL_DEPRECATIONS=${TEMPEST_FATAL_DEPRECATIONS:-"no"}

# Ubuntu repos
UBUNTU_RELEASE=$(lsb_release -sc)
UBUNTU_REPO=${UBUNTU_REPO:-"http://mirror.rackspace.com/ubuntu"}
UBUNTU_SEC_REPO=${UBUNTU_SEC_REPO:-"http://mirror.rackspace.com/ubuntu"}


## Library Check -------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh


## Main ----------------------------------------------------------------------

# Make the /openstack/log directory for openstack-infra gate check log publishing
mkdir -p /openstack/log

# Implement the log directory link for openstack-infra log publishing
ln -sf /openstack/log $SYMLINK_DIR

# Create ansible logging directory and add in a log file entry into ansible.cfg
if [ -f "playbooks/ansible.cfg" ];then
  mkdir -p /openstack/log/ansible-logging
  if [ ! "$(grep -e '^log_path\ =\ /openstack/log/ansible-logging/ansible.log' playbooks/ansible.cfg)" ];then
    sed -i '/\[defaults\]/a log_path = /openstack/log/ansible-logging/ansible.log' playbooks/ansible.cfg
  fi
fi

# Check that the link creation was successful
[[ -d $SYMLINK_DIR ]] || exit_fail
if ! [ -d $SYMLINK_DIR ] ; then
    echo "Could not create a link from /openstack/log to ${SYMLINK_DIR}"
    exit_fail
fi

# Log some data about the instance and the rest of the system
log_instance_info

# Ensure that the current kernel can support vxlan
if ! modprobe vxlan; then
  MINIMUM_KERNEL_VERSION=$(awk '/openstack_host_required_kernel/ {print $2}' playbooks/inventory/group_vars/all.yml)
  echo "A minimum kernel version of ${MINIMUM_KERNEL_VERSION} is required for vxlan support."
  echo "This build will not work without it."
  exit_fail
fi

info_block "Running AIO Setup"

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

# Flush all the iptables rules set by openstack-infra
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
if grep "^PermitRootLogin" /etc/ssh/sshd_config > /dev/null; then
  sed -i 's/^PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
else
  echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
fi

# Create /opt if it doesn't already exist
if [ ! -d "/opt" ];then
  mkdir /opt
fi

# Remove the pip directory if its found
if [ -d "${HOME}/.pip" ];then
  rm -rf "${HOME}/.pip"
fi

# Install pip
if [ ! "$(which pip)" ];then
    curl ${GET_PIP_URL} > /opt/get-pip.py
    python2 /opt/get-pip.py || python /opt/get-pip.py
fi

# Install requirements if there are any
if [ -f "requirements.txt" ];then
    pip2 install -r requirements.txt || pip install -r requirements.txt
fi

# Configure all disk space
configure_diskspace

# Create /etc/rc.local if it doesn't already exist
if [ ! -f "/etc/rc.local" ];then
  touch /etc/rc.local
  chmod +x /etc/rc.local
fi

# Make the system key used for bootstrapping self
if [ ! -d /root/.ssh ];then
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh
fi

ssh_key_create

# Make sure everything is mounted.
mount -a || true

# Build the loopback drive for swap to use
if [ ! "$(swapon -s | grep -v Filename)" ]; then
  memory_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
  if [ "${memory_kb}" -lt "8388608" ]; then
    swap_size="4294967296"
  else
    swap_size="8589934592"
  fi
  loopback_create "/opt/swap.img" ${swap_size} thick swap
  # Ensure swap will be used on the host
  if [ ! $(sysctl vm.swappiness | awk '{print $3}') == "10" ];then
    sysctl -w vm.swappiness=10 | tee -a /etc/sysctl.conf
  fi
  swapon -a
fi

# Build the loopback drive for cinder to use
CINDER="cinder.img"
if ! vgs cinder-volumes; then
  loopback_create "/opt/${CINDER}" 1073741824000 thin rc
  CINDER_DEVICE=$(losetup -a | awk -F: "/${CINDER}/ {print \$1}")
  pvcreate ${CINDER_DEVICE}
  pvscan
  # Check for the volume group
  if ! vgs cinder-volumes; then
    vgcreate cinder-volumes ${CINDER_DEVICE}
  fi
  # Ensure that the cinder loopback is enabled after reboot
  if ! grep ${CINDER} /etc/rc.local && ! vgs cinder-volumes; then
    sed -i "\$i losetup \$(losetup -f) /opt/${CINDER}" /etc/rc.local
  fi
fi

# Enable swift deployment
if [ "${DEPLOY_SWIFT}" == "yes" ]; then
  # build the loopback drives for swift to use
  for SWIFT in swift1 swift2 swift3; do
    if ! grep "${SWIFT}" /proc/mounts > /dev/null; then
      loopback_create "/opt/${SWIFT}.img" 1073741824000 thin none
      if ! grep -w "^/opt/${SWIFT}.img" /etc/fstab > /dev/null; then
        echo "/opt/${SWIFT}.img /srv/${SWIFT}.img xfs loop,noatime,nodiratime,nobarrier,logbufs=8 0 0" >> /etc/fstab
      fi
      # Format the lo devices
      mkfs.xfs -f "/opt/${SWIFT}.img"
      mkdir -p "/srv/${SWIFT}.img"
      mount "/opt/${SWIFT}.img" "/srv/${SWIFT}.img"
    fi
  done
fi

# Copy aio network config into place.
if [ ! -d "/etc/network/interfaces.d" ];then
  mkdir -p /etc/network/interfaces.d/
fi

# Copy the basic aio network interfaces over
cp -R etc/network/interfaces.d/aio_interfaces.cfg /etc/network/interfaces.d/

# Ensure the network source is in place
if [ ! "$(grep -Rni '^source\ /etc/network/interfaces.d/\*.cfg' /etc/network/interfaces)" ]; then
    echo "source /etc/network/interfaces.d/*.cfg" | tee -a /etc/network/interfaces
fi

# Bring up the new interfaces
for i in $(awk '/^iface/ {print $2}' /etc/network/interfaces.d/aio_interfaces.cfg); do
    if grep "^$i\:" /proc/net/dev > /dev/null;then
      /sbin/ifdown $i || true
    fi
    /sbin/ifup $i || true
done

# Remove an existing etc directory if already found
if [ -d "/etc/openstack_deploy" ];then
  rm -rf "/etc/openstack_deploy"
fi

# Move the *.aio files into place for use within the AIO build.
cp -R etc/openstack_deploy /etc/
for i in $(find /etc/openstack_deploy/ -type f -name '*.aio');do
  rename 's/\.aio$//g' $i
done

# Ensure the conf.d directory exists
if [ ! -d "/etc/openstack_deploy/conf.d" ];then
  mkdir -p "/etc/openstack_deploy/conf.d"
fi

# Generate the passwords
scripts/pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml

# change the generated passwords for the OpenStack (admin)
sed -i "s/keystone_auth_admin_password:.*/keystone_auth_admin_password: ${ADMIN_PASSWORD}/" /etc/openstack_deploy/user_secrets.yml
sed -i "s/external_lb_vip_address:.*/external_lb_vip_address: ${PUBLIC_ADDRESS}/" /etc/openstack_deploy/openstack_user_config.yml

# Service region set
echo "keystone_service_region: ${SERVICE_REGION}" | tee -a /etc/openstack_deploy/user_variables.yml

# Virt type set
echo "nova_virt_type: ${NOVA_VIRT_TYPE}" | tee -a /etc/openstack_deploy/user_variables.yml

# Set network for tempest
echo "tempest_public_subnet_cidr: ${TEMPEST_FLAT_CIDR}" | tee -a /etc/openstack_deploy/user_variables.yml

# Minimize galera cache
echo 'galera_gcache_size: 32M' | tee -a /etc/openstack_deploy/user_variables.yml
echo 'galera_innodb_buffer_pool_size: 512M' | tee -a /etc/openstack_deploy/user_variables.yml
echo 'galera_innodb_log_buffer_size: 32M' | tee -a /etc/openstack_deploy/user_variables.yml

# Set the running kernel as the required kernel
echo "required_kernel: $(uname --kernel-release)" | tee -a /etc/openstack_deploy/user_variables.yml

# Set the Ubuntu apt repository used for containers to the same as the host
echo "lxc_container_template_main_apt_repo: ${UBUNTU_REPO}" | tee -a /etc/openstack_deploy/user_variables.yml
echo "lxc_container_template_security_apt_repo: ${UBUNTU_REPO}" | tee -a /etc/openstack_deploy/user_variables.yml

# Set the running neutron workers to 0/1
echo "neutron_api_workers: 0" | tee -a /etc/openstack_deploy/user_variables.yml
echo "neutron_rpc_workers: 0" | tee -a /etc/openstack_deploy/user_variables.yml
echo "neutron_metadata_workers: 1" | tee -a /etc/openstack_deploy/user_variables.yml

# Add in swift vars if needed
if [ "${DEPLOY_SWIFT}" == "yes" ]; then
  # ensure that glance is configured to use swift
  sed -i "s/glance_default_store:.*/glance_default_store: swift/" /etc/openstack_deploy/user_variables.yml
  echo "cinder_service_backup_program_enabled: True" | tee -a /etc/openstack_deploy/user_variables.yml
  echo "tempest_volume_backup_enabled: True" | tee -a /etc/openstack_deploy/user_variables.yml
fi

if [ ! -z "${RABBITMQ_PACKAGE_URL}" ]; then
  echo "rabbitmq_package_url: ${RABBITMQ_PACKAGE_URL}" | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Update fatal_deprecations settings
if [ "${CINDER_FATAL_DEPRECATIONS}" == "yes" ]; then
  echo "cinder_fatal_deprecations: True" | tee -a /etc/openstack_deploy/user_variables.yml
fi

if [ "${GLANCE_FATAL_DEPRECATIONS}" == "yes" ]; then
  echo "glance_fatal_deprecations: True" | tee -a /etc/openstack_deploy/user_variables.yml
fi

if [ "${HEAT_FATAL_DEPRECATIONS}" == "yes" ]; then
  echo "heat_fatal_deprecations: True" | tee -a /etc/openstack_deploy/user_variables.yml
fi

if [ "${KEYSTONE_FATAL_DEPRECATIONS}" == "yes" ]; then
  echo "keystone_fatal_deprecations: True" | tee -a /etc/openstack_deploy/user_variables.yml
fi

if [ "${NEUTRON_FATAL_DEPRECATIONS}" == "yes" ]; then
  echo "neutron_fatal_deprecations: True" | tee -a /etc/openstack_deploy/user_variables.yml
fi

if [ "${NOVA_FATAL_DEPRECATIONS}" == "yes" ]; then
  echo "nova_fatal_deprecations: True" | tee -a /etc/openstack_deploy/user_variables.yml
fi

if [ "${TEMPEST_FATAL_DEPRECATIONS}" == "yes" ]; then
  echo "tempest_fatal_deprecations: True" | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Log some data about the instance and the rest of the system
log_instance_info

info_block "The system has been prepared for an all-in-one build."
