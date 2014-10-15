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
set -e -u -v -x

REPO_URL=${REPO_URL:-"https://github.com/rcbops/ansible-lxc-rpc.git"}
REPO_BRANCH=${REPO_BRANCH:-"master"}
FROZEN_REPO_URL=${FROZEN_REPO_URL:-"http://rpc-slushee.rackspace.com"}
MAX_RETRIES=${MAX_RETRIES:-5}

apt-get update
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
                   linux-image-extra-$(uname -r)

function key_create(){
  ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''
}

# Used to retry process that may fail due to random issues.
function successerator() {
  set +e
  RETRY=0
  # Set the initial return value to failure
  false
 
  while [ $? -ne 0 -a ${RETRY} -lt ${MAX_RETRIES} ];do
    RETRY=$((${RETRY}+1))
    $@
  done
 
  if [ ${RETRY} -eq ${MAX_RETRIES} ];then
    echo "Hit maximum number of retries, giving up..."
    exit 1
  fi
  set -e
}

function install_bits() {
  successerator ansible-playbook -e @/etc/rpc_deploy/user_variables.yml \
                                 playbooks/$@
}

if [ ! -d "/opt" ];then
  mkdir /opt
fi
 
 
if [ ! "$(swapon -s | grep -v Filename)" ];then
  cat > /opt/swap.sh <<EOF
#!/usr/bin/env bash
if [ ! "\$(swapon -s | grep -v Filename)" ];then
SWAPFILE="/tmp/SwapFile"
if [ -f "\${SWAPFILE}" ];then
  swapoff -a
  rm \${SWAPFILE}
fi
dd if=/dev/zero of=\${SWAPFILE} bs=1M count=512
mkswap \${SWAPFILE}
swapon \${SWAPFILE}
fi
EOF
 
  chmod +x /opt/swap.sh
  /opt/swap.sh
fi
 
if [ -f "/opt/swap.sh" ];then
  if [ ! -f "/etc/rc.local" ];then
    touch /etc/rc.local
  fi
 
  if [ "$(grep 'exit 0' /etc/rc.local)" ];then
    sed -i '/exit\ 0/ s/^/#\ /' /etc/rc.local
  fi
  
  if [ ! "$(grep 'swap.sh' /etc/rc.local)" ];then 
    echo "/opt/swap.sh" | tee -a /etc/rc.local
  fi
  
  chmod +x /etc/rc.local
fi

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

CINDER="/opt/cinder.img"
if [ ! "$(losetup -a | grep /opt/cinder.img)" ];then
  LOOP=$(losetup -f)
  dd if=/dev/zero of=${CINDER} bs=1 count=0 seek=1000G
  losetup ${LOOP} ${CINDER}
  pvcreate ${LOOP}
  vgcreate cinder-volumes ${LOOP}
  pvscan
fi

# Get the source
if [ -d "/opt/ansible-lxc-rpc" ];then
  rm -rf "/opt/ansible-lxc-rpc"
fi
git clone "${REPO_URL}" "/opt/ansible-lxc-rpc"

pushd /opt/ansible-lxc-rpc
  git checkout "${REPO_BRANCH}"
  # Copy the base etc files
  if [ -d "/etc/rpc_deploy" ];then
    rm -rf "/etc/rpc_deploy"
  fi
  cp -R /opt/ansible-lxc-rpc/etc/rpc_deploy /etc/
  # Install pip
  curl ${FROZEN_REPO_URL}/downloads/get-pip.py | python
  # Install requirements
  pip install -r /opt/ansible-lxc-rpc/requirements.txt
  # Generate the passwords
  /opt/ansible-lxc-rpc/scripts/pw-token-gen.py --file /etc/rpc_deploy/user_variables.yml
popd

cat > /etc/rpc_deploy/user_variables.yml <<EOF
---
rpc_repo_url: ${FROZEN_REPO_URL}
required_kernel: 3.13.0-30-generic
## Rackspace Cloud Details
rackspace_cloud_auth_url: https://identity.api.rackspacecloud.com/v2.0
rackspace_cloud_tenant_id: SomeTenantID
rackspace_cloud_username: SomeUserName
rackspace_cloud_password: SomeUsersPassword
rackspace_cloud_api_key: SomeAPIKey
## Rabbit Options
rabbitmq_password: secrete
rabbitmq_cookie_token: secrete
## Tokens
memcached_encryption_key: secrete
## Container default user
container_openstack_password: secrete
## Galera Options
mysql_root_password: secrete
mysql_debian_sys_maint_password: secrete
## Keystone Options
keystone_container_mysql_password: secrete
keystone_auth_admin_token: secrete
keystone_auth_admin_password: secrete
keystone_service_password: secrete
## Cinder Options
cinder_container_mysql_password: secrete
cinder_service_password: secrete
cinder_v2_service_password: secrete
# Set default_store to "swift" if using Cloud Files or swift backend
glance_default_store: file
glance_container_mysql_password: secrete
glance_service_password: secrete
glance_swift_store_auth_address: "{{ rackspace_cloud_auth_url }}"
glance_swift_store_user: "{{ rackspace_cloud_tenant_id }}:{{ rackspace_cloud_username }}"
glance_swift_store_key: "{{ rackspace_cloud_password }}"
glance_swift_store_container: SomeContainerName
glance_swift_store_region: SomeRegion
glance_swift_store_endpoint_type: internalURL
glance_notification_driver: noop
## Heat Options
heat_stack_domain_admin_password: secrete
heat_container_mysql_password: secrete
### THE HEAT AUTH KEY NEEDS TO BE 32 CHARACTERS LONG ##
heat_auth_encryption_key: 12345678901234567890123456789012
### THE HEAT AUTH KEY NEEDS TO BE 32 CHARACTERS LONG ##
heat_service_password: secrete
heat_cfn_service_password: secrete
## Horizon Options
horizon_container_mysql_password: secrete
## MaaS Options
maas_auth_method: password
maas_auth_url: "{{ rackspace_cloud_auth_url }}"
maas_username: "{{ rackspace_cloud_username }}"
maas_api_key: "{{ rackspace_cloud_api_key }}"
maas_auth_token: some_token
maas_api_url: https://monitoring.api.rackspacecloud.com/v1.0/{{ rackspace_cloud_tenant_id }}
maas_notification_plan: npTechnicalContactsEmail
# By default we will create an agent token for each entity, however if you'd
# prefer to use the same agent token for all entities then specify it here
#maas_agent_token: some_token
maas_target_alias: public0_v4
maas_scheme: https
# Override scheme for specific service remote monitor by specifying here: E.g.
# maas_nova_scheme: http
maas_keystone_user: maas
maas_keystone_password: secrete
# Check this number of times before registering state change
maas_alarm_local_consecutive_count: 3
maas_alarm_remote_consecutive_count: 1
# Timeout must be less than period
maas_check_period: 60
maas_check_timeout: 30
maas_monitoring_zones:
  - mzdfw
  - mziad
  - mzord
  - mzlon
  - mzhkg
maas_repo_version: v9.0.0
## Neutron Options
neutron_container_mysql_password: secrete
neutron_service_password: secrete
## Nova Options
nova_virt_type: qemu
nova_container_mysql_password: secrete
nova_metadata_proxy_secret: secrete
nova_ec2_service_password: secrete
nova_service_password: secrete
nova_v3_service_password: secrete
nova_s3_service_password: secrete
## RPC Support
rpc_support_holland_password: secrete
## Kibana Options
kibana_password: secrete
EOF


cat > /etc/rpc_deploy/rpc_user_config.yml <<EOF
---
# This is the md5 of the environment file
environment_version: $(md5sum /etc/rpc_deploy/rpc_environment.yml | awk '{print $1}')
# User defined CIDR used for containers
cidr_networks:
  # Cidr used in the Management network
  container: 172.29.236.0/22
  # Cidr used in the Service network
  snet: 172.29.248.0/22
  # Cidr used in the VM network
  tunnel: 172.29.240.0/22
  # Cidr used in the Storage network
  storage: 172.29.244.0/22
used_ips:
  - 172.29.236.1,172.29.236.50
  - 172.29.244.1,172.29.244.50
global_overrides:
  rpc_repo_url: ${FROZEN_REPO_URL}
  # Internal Management vip address
  internal_lb_vip_address: 172.29.236.100
  # External DMZ VIP address
  external_lb_vip_address: 10.200.200.146
  # Bridged interface to use with tunnel type networks
  tunnel_bridge: "br-vxlan"
  # Bridged interface to build containers with
  management_bridge: "br-mgmt"
  # Define your Add on container networks.
  provider_networks:
    - network:
        group_binds:
          - all_containers
          - hosts
        type: "raw"
        container_bridge: "br-mgmt"
        container_interface: "eth1"
        ip_from_q: "container"
    - network:
        group_binds:
          - glance_api
          - cinder_api
          - cinder_volume
          - nova_compute
        type: "raw"
        container_bridge: "br-storage"
        container_interface: "eth2"
        ip_from_q: "storage"
    - network:
        group_binds:
          - glance_api
          - nova_compute
          - neutron_linuxbridge_agent
        type: "raw"
        container_bridge: "br-snet"
        container_interface: "eth3"
        ip_from_q: "snet"
    - network:
        group_binds:
          - neutron_linuxbridge_agent
        container_bridge: "br-vxlan"
        container_interface: "eth10"
        ip_from_q: "tunnel"
        type: "vxlan"
        range: "1:1000"
        net_name: "vxlan"
    - network:
        group_binds:
          - neutron_linuxbridge_agent
        container_bridge: "br-vlan"
        container_interface: "eth11"
        type: "flat"
        net_name: "vlan"
    - network:
        group_binds:
          - neutron_linuxbridge_agent
        container_bridge: "br-vlan"
        container_interface: "eth11"
        type: "vlan"
        range: "1:1"
        net_name: "vlan"
  # Name of load balancer
  lb_name: lb_name_in_core
# User defined Infrastructure Hosts, this should be a required group
infra_hosts:
  aio1:
    ip: 172.29.236.100
# User defined Compute Hosts, this should be a required group
compute_hosts:
  aio1:
    ip: 172.29.236.100
# User defined Storage Hosts, this should be a required group
storage_hosts:
  aio1:
    ip: 172.29.236.100
    container_vars:
      cinder_backends:
        limit_container_types: cinder_volume
        lvm:
          volume_group: cinder-volumes
          volume_driver: cinder.volume.drivers.lvm.LVMISCSIDriver
          volume_backend_name: LVM_iSCSI
# User defined Logging Hosts, this should be a required group
log_hosts:
  aio1:
    ip: 172.29.236.100
# User defined Networking Hosts, this should be a required group
network_hosts:
  aio1:
    ip: 172.29.236.100
haproxy_hosts:
  aio1:
    ip: 172.29.236.100
EOF


cat > /etc/network/interfaces.d/aio-bridges.cfg <<EOF
## Required network bridges; br-vlan, br-vxlan, br-mgmt.
auto br-mgmt
iface br-mgmt inet static
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
    # Notice the bridge port is the vlan tagged interface
    bridge_ports none
    address 172.29.236.100
    netmask 255.255.252.0

auto br-vxlan
iface br-vxlan inet static
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
    bridge_ports none
    address 172.29.240.100
    netmask 255.255.252.0

auto br-vlan
iface br-vlan inet manual
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
    # Notice this bridge port is an Untagged host interface
    bridge_ports none

auto br-storage
iface br-storage inet static
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
    bridge_ports none
    address 172.29.244.100
    netmask 255.255.252.0

auto br-snet
iface br-snet inet static
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
    bridge_ports none
    # Notice there is NO physical interface in this bridge!
    address 172.29.248.100
    netmask 255.255.252.0
EOF

# Ensure the network source is in place
if [ ! "$(grep -Rni '^source\ /etc/network/interfaces.d/\*.cfg' /etc/network/interfaces)" ]; then
    echo "source /etc/network/interfaces.d/*.cfg" | tee -a /etc/network/interfaces
fi

# Bring up the new interfaces
for i in br-snet br-storage br-vlan br-vxlan br-mgmt; do
    /sbin/ifup $i || true
done

# Export the home directory just in case it's not set
export HOME="/root"
pushd /opt/ansible-lxc-rpc/rpc_deployment
  # Install all host bits
  install_bits setup/host-setup.yml
  # Install haproxy for dev purposes only
  install_bits infrastructure/haproxy-install.yml
  # Install all of the infra bits
  install_bits infrastructure/infrastructure-setup.yml
  # install all of the Openstack Bits
  install_bits openstack/openstack-common.yml
  install_bits openstack/keystone.yml
  install_bits openstack/keystone-add-all-services.yml
  install_bits openstack/glance-all.yml
  install_bits openstack/heat-all.yml
  install_bits openstack/nova-all.yml
  install_bits openstack/neutron-all.yml
  install_bits openstack/cinder-all.yml
  install_bits openstack/horizon-all.yml
  install_bits openstack/utility.yml
  install_bits openstack/rpc-support.yml
  # Stop rsyslog container(s)
  for i in $(lxc-ls | grep "rsyslog"); do 
      lxc-stop -k -n $i; lxc-start -d -n $i
  done
  # Reconfigure Rsyslog
  install_bits infrastructure/rsyslog-config.yml
popd

if [ ! "$(dpkg -l | grep linux-image-extra-3.13.0-35-generic)" ];then
    apt-get install -y linux-image-extra-3.13.0-35-generic
    rm /etc/update-motd.d/*
cat > /etc/update-motd.d/00-rpc-notice<< EOF
#!/usr/bin/env bash
echo ""
echo "############ RPC DEPLOYMENT #############"
echo "A new kernel was installed on this system. you will"
echo "need to re-bootstrap Galera to get the cluster operataional."
echo "from the /opt/ansible-lxc-rpc/rpc_deployment directory execute:"
echo ""
echo "ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/infrastructure/galera-startup.yml"
EOF
chmod +x /etc/update-motd.d/00-rpc-notice
shutdown -r now
fi
