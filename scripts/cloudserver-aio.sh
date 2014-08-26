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
#
# (c) 2014, Kevin Carter <kevin.carter@rackspace.com>


# Assumptions:
# This assumes that the lab environment will be setup using
# a rackspace cloud server build on the rackspace public cloud.
# The lab will attempt to create the required Volume Groups that
# the lab will want to use as it creates your containers, if
# /dev/xvde is not available all containers will be created using
# the local file system.  If /dev/xvde is available it WILL BE
# NUKED and partitioned for the environment. Once the partitioning is
# done the lab will create all of the required containers as well as
# anything else that may be needed prior to running the installation.
# If using LVM you should have NO LESS than 100 GB of consumable space
# on your the /dev/xvde device.  If you have less than 100G the installation
# will fail.

# THIS IS NOT FOR PRODUCTION USE, NOR WILL IT EVER BE. This is a simple
# lab setup tool that will allow you to quickly build an ALL IN ONE
# environment for development purposes.


set -e -u -v -x

LAB_NAME=${LAB_NAME:-ansible-lxc-rpc-inventory}
LAB_LV_DEVICE=${LAB_LV_DEVICE:-/dev/xvde}
LAB_BRIDGE_INTERFACE=${LAB_BRIDGE_INTERFACE:-br-mgmt}
LAB_MAIN_INTERFACE=${LAB_MAIN_INTERFACE:-eth0}

function key_create(){
  ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''
}

# Make the system key used for bootstrapping self
pushd /root/.ssh/
if [ ! -f "id_rsa" ];then
    key_create
fi

if [ ! -f "id_rsa.pub" ];then
  rm "id_rsa"
  key_create
fi

KEYENTRY=$(cat id_rsa.pub)
if [ ! "$(grep \"$KEYENTRY\" authorized_keys)" ];then
    echo "$KEYENTRY" | tee -a authorized_keys
fi
popd

# Install base System Packages
apt-get update && apt-get install -y python-dev \
                                     build-essential \
                                     curl \
                                     git-core \
                                     ipython \
                                     tmux \
                                     vim
apt-get -y upgrade

# If Ephemeral disk is detected carve it up as LVM
if [ -e "${LAB_LV_DEVICE}" ];then
  SPACE=$(parted -s /dev/xvde p | awk '/Disk/ {print $3}' | grep -o '[0-9]\+')
  ENOUGH_SPACE=$(python -c "o=\"$SPACE\".split('.')[0]; print(int(o) > 100)")
  if [ "$ENOUGH_SPACE" == True ];then
    apt-get update && apt-get install -y lvm2
    if [ ! "$(echo C | parted ${LAB_LV_DEVICE} p | grep gpt)" ];then
      parted -s ${LAB_LV_DEVICE} mktable gpt
      parted -s ${LAB_LV_DEVICE} mkpart lvm 0% 90%
      parted -s ${LAB_LV_DEVICE} mkpart lvm 90% 100%
    fi
    if [ ! "$(pvs | grep '/dev/xvde1')" ];then
      pvcreate ${LAB_LV_DEVICE}1
      vgcreate lxc ${LAB_LV_DEVICE}1
    fi
    if [ ! "$(pvs | grep '/dev/xvde2')" ];then
      pvcreate ${LAB_LV_DEVICE}2
      vgcreate cinder-volumes ${LAB_LV_DEVICE}2
    fi
  else
    CINDER="/opt/cinder.img"
    if [ ! "$(losetup -a | grep /opt/cinder.img)" ];then
      LOOP=$(losetup -f)
      dd if=/dev/zero of=${CINDER} bs=1 count=0 seek=1000G
      losetup ${LOOP} ${CINDER}
      pvcreate ${LOOP}
      vgcreate cinder-volumes ${LOOP}
      pvscan
    fi
  fi
fi

# Get modern pip
curl https://bootstrap.pypa.io/get-pip.py | python

# Install ansible
pip install ansible==1.6.6

# Get our playbooks
if [ ! -d /opt/ansible-lxc-rpc ]; then
    git clone https://github.com/rcbops/ansible-lxc-rpc /opt/ansible-lxc-rpc
fi

# Get the eth0 IP address
MAINADDR="$(ip route show dev ${LAB_MAIN_INTERFACE} | awk '{print $7}' | tail -n 1)"

# Get the eth2 CIDR
VIPADDR="$(ip route show dev ${LAB_BRIDGE_INTERFACE} | awk '{print $7}' | tail -n 1)"

cp -R /opt/ansible-lxc-rpc/etc/rpc_deploy /etc/rpc_deploy

cat > /etc/rpc_deploy/rpc_user_config.yml <<EOF
---
# User defined CIDR used for containers
cidr: $VIPADDR/24

# User defined Infrastructure Hosts
infra_hosts:
  aio1:
    ip: $MAINADDR

# User defined Compute Hosts
compute_hosts:
  aio1:
    ip: $MAINADDR

# User defined Storage Hosts
storage_hosts:
  aio1:
    ip: $MAINADDR

# User defined Network Hosts
network_hosts:
  aio1:
    ip: $MAINADDR

# User defined Logging Hosts
log_hosts:
  aio1:
    ip: $MAINADDR

## Other hosts can be added whenever needed.
haproxy_hosts:
  aio1:
    ip: $MAINADDR
EOF

sed -i "s/internal_lb_vip_address:.*/internal_lb_vip_address: ${VIPADDR}/" /opt/ansible-lxc-rpc/rpc_deployment/vars/user_variables.yml

# Install all the things
pushd /opt/ansible-lxc-rpc
    # Ensure that the scripts python requirements are installed
    pip install -r requirements.txt
    pushd /opt/ansible-lxc-rpc/rpc_deployment
      # Base Setup
      ansible-playbook -e @/opt/ansible-lxc-rpc/rpc_deployment/vars/user_variables.yml playbooks/setup/all-the-setup-things.yml

      # Infrastructure Setup
      ansible-playbook -e @/opt/ansible-lxc-rpc/rpc_deployment/vars/user_variables.yml playbooks/infrastructure/all-the-infrastructure-things.yml

      # Openstack Service Setup
      ansible-playbook -e @/opt/ansible-lxc-rpc/rpc_deployment/vars/user_variables.yml playbooks/openstack/all-the-openstack-things.yml
    popd
popd
