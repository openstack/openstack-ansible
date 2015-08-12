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


## Variables -----------------------------------------------------------------
DEPLOY_HOST=${DEPLOY_HOST:-"yes"}
DEPLOY_LB=${DEPLOY_LB:-"yes"}
DEPLOY_INFRASTRUCTURE=${DEPLOY_INFRASTRUCTURE:-"yes"}
DEPLOY_LOGGING=${DEPLOY_LOGGING:-"yes"}
DEPLOY_OPENSTACK=${DEPLOY_OPENSTACK:-"yes"}
DEPLOY_SWIFT=${DEPLOY_SWIFT:-"yes"}
DEPLOY_CEILOMETER=${DEPLOY_CEILOMETER:-"yes"}
DEPLOY_TEMPEST=${DEPLOY_TEMPEST:-"no"}
COMMAND_LOGS=${COMMAND_LOGS:-"/openstack/log/ansible_cmd_logs/"}
ADD_NEUTRON_AGENT_CHECKSUM_RULE=${BOOTSTRAP_AIO:-"no"}


## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh


## Main ----------------------------------------------------------------------
# Create a simple task to bounce all networks within a container.
cat > /tmp/ensure_container_networking.sh <<EOF
#!/usr/bin/env bash
INTERFACES=""
INTERFACES+="\$(awk '/auto/ {print \$2}' /etc/network/interfaces) "
INTERFACES+="\$(ls -1 /etc/network/interfaces.d/ | awk -F'.cfg' '{print \$1}')"
for i in \${INTERFACES}; do
  echo "Bouncing on \$i"
  ifdown \$i || true
  ifup \$i || true
done
EOF

# Initiate the deployment
pushd "playbooks"
  if [ "${DEPLOY_HOST}" == "yes" ]; then
    # Install all host bits
    install_bits openstack-hosts-setup.yml
    install_bits lxc-hosts-setup.yml

    # Bring the lxc bridge down and back up to ensures the iptables rules are in-place
    # This also will ensure that the lxc dnsmasq rules are active.
    mkdir -p "${COMMAND_LOGS}/host_net_bounce"
    ansible hosts -m shell \
                  -a '(ifdown lxcbr0 || true); ifup lxcbr0' \
                  -t "${COMMAND_LOGS}/host_net_bounce" \
                  &> ${COMMAND_LOGS}/host_net_bounce.log

    # Restart any containers that may already exist
    mkdir -p "${COMMAND_LOGS}/lxc_existing_container_restart"
    ansible hosts -m shell \
                  -a 'for i in $(lxc-ls); do lxc-stop -n $i; lxc-start -d -n $i; done' \
                  -t "${COMMAND_LOGS}/lxc_existing_container_restart" \
                  &> ${COMMAND_LOGS}/lxc_existing_container_restart.log

    # Create the containers.
    install_bits lxc-containers-create.yml

    # Make sure there are no dead veth(s)
    # This is good when using a host with multiple times, IE: Rebuilding.
    mkdir -p "${COMMAND_LOGS}/veth_cleanup"
    ansible hosts -m shell \
                  -a 'lxc-system-manage veth-cleanup' \
                  -t "${COMMAND_LOGS}/veth_cleanup" \
                  &> ${COMMAND_LOGS}/veth_cleanup.log

    # Flush the net cache
    # This is good when using a host with multiple times, IE: Rebuilding.
    mkdir -p "${COMMAND_LOGS}/flush_net_cache"
    ansible hosts -m shell \
                  -a 'lxc-system-manage flush-net-cache' \
                  -t "${COMMAND_LOGS}/flush_net_cache" \
                  &> ${COMMAND_LOGS}/flush_net_cache.log

    # Log some data about the instance and the rest of the system
    log_instance_info

    # Force the networks down and then up
    mkdir -p "${COMMAND_LOGS}/container_net_bounce"
    ansible all_containers -m script \
                           -a '/tmp/ensure_container_networking.sh' \
                           --forks ${FORKS} \
                           -t "${COMMAND_LOGS}/container_net_bounce" \
                           &> ${COMMAND_LOGS}/container_net_bounce.log

    # Force an apt-cache update for packages and keys throttling the processes.
    #  * Note: that the task will always return 0. We want to see everything and
    #          if it fails we want to see where it breaks down within the stack.
    #  * Note: this is not using the apt module, because we want to FORCE it with raw.
    mkdir -p "${COMMAND_LOGS}/force_apt_update"
    ansible all_containers -m raw \
                           -a '(apt-get update && apt-key update) || true' \
                           --forks ${FORKS} \
                           -t "${COMMAND_LOGS}/force_apt_update" \
                           &> ${COMMAND_LOGS}/force_apt_update.log

    # When running in an AIO, we need to drop the following iptables rule in any neutron_agent containers
    # to that ensure instances can communicate with the neutron metadata service.
    # This is necessary because in an AIO environment there are no physical interfaces involved in
    # instance -> metadata requests, and this results in the checksums being incorrect.
    if [ "${ADD_NEUTRON_AGENT_CHECKSUM_RULE}" == "yes" ]; then
      mkdir -p "${COMMAND_LOGS}/add_neutron_agent_checksum_rule"
      ansible neutron_agent -m command \
                            -a '/sbin/iptables -t mangle -A POSTROUTING -p tcp --sport 80 -j CHECKSUM --checksum-fill' \
                            -t "${COMMAND_LOGS}/add_neutron_agent_checksum_rule" \
                            &> ${COMMAND_LOGS}/add_neutron_agent_checksum_rule.log
      ansible neutron_agent -m shell \
                            -a 'DEBIAN_FRONTEND=noninteractive apt-get install iptables-persistent' \
                            -t "${COMMAND_LOGS}/add_neutron_agent_checksum_rule" \
                            &>> ${COMMAND_LOGS}/add_neutron_agent_checksum_rule.log
    fi
  fi

  if [ "${DEPLOY_LB}" == "yes" ]; then
    # Install haproxy for dev purposes only
    install_bits haproxy-install.yml
  fi

  if [ "${DEPLOY_INFRASTRUCTURE}" == "yes" ]; then
    # Install all of the infra bits
    install_bits memcached-install.yml

    # For the purposes of gating the repository of python wheels are built within
    # the environment. Normal installation would simply clone the upstream mirror.
    install_bits repo-server.yml
    install_bits repo-build.yml
    mkdir -p "${COMMAND_LOGS}/repo_data"
    ansible 'repo_all[0]' -m raw \
                          -a 'find  /var/www/repo/os-releases -type l' \
                          -t "${COMMAND_LOGS}/repo_data"

    install_bits galera-install.yml
    install_bits rabbitmq-install.yml
    install_bits utility-install.yml

    if [ "${DEPLOY_LOGGING}" == "yes" ]; then
      install_bits rsyslog-install.yml
    fi
  fi

  if [ "${DEPLOY_OPENSTACK}" == "yes" ]; then
    # install all of the compute Bits
    install_bits os-keystone-install.yml
    install_bits os-glance-install.yml
    install_bits os-cinder-install.yml
    install_bits os-nova-install.yml
    install_bits os-neutron-install.yml
    install_bits os-heat-install.yml
    install_bits os-horizon-install.yml
  fi

  # If ceilometer is deployed, it must be run before
  # swift, since the swift playbooks will make reference
  # to the ceilometer user when applying the reselleradmin
  # role
  if [ "${DEPLOY_CEILOMETER}" == "yes" ]; then
    install_bits os-ceilometer-install.yml
  fi

  if [ "${DEPLOY_SWIFT}" == "yes" ]; then
    if [ "${DEPLOY_OPENSTACK}" == "no" ]; then
      # When os install is no, make sure we still have keystone for use in swift.
      install_bits os-keystone-install.yml
    fi
    # install all of the swift Bits
    install_bits os-swift-install.yml
  fi

  if [ "${DEPLOY_TEMPEST}" == "yes" ]; then
    # Deploy tempest
    install_bits os-tempest-install.yml
  fi

popd

# print the report data
set +x && print_report
