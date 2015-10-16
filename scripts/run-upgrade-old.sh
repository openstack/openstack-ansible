#!/usr/bin/env bash
# Copyright 2015, Rackspace US, Inc.
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

## Pre-flight Check ----------------------------------------------------------
# Clear the screen and make sure the user understands whats happening.
clear

# NOTICE: To run this in an automated fashion run the script via
#   root@HOSTNAME:/opt/openstack-ansible# echo "YES" | bash scripts/run-upgrade.sh

# Notify the user.
echo -e "
This script will perform a v10.x to v11.x upgrade.
Once you start the upgrade there's no going back.

Note, this is an online upgrade and while the
in progress running VMs will not be impacted.
However, you can expect some hiccups with OpenStack
API services while the upgrade is running.

Are you ready to perform this upgrade now?
"

# Confirm the user is ready to upgrade.
read -p 'Enter "YES" to continue or anything else to quit: ' UPGRADE
if [ "${UPGRADE}" == "YES" ]; then
  echo "Running Upgrade from v10.x to v11.x"
else
  exit 99
fi

## Shell Opts ----------------------------------------------------------------
set -e -u -v

## Library Check -------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh

## Functions -----------------------------------------------------------------
function get_inv_items {
  ./scripts/inventory-manage.py -f /etc/openstack_deploy/openstack_inventory.json -l | grep -w ".*$1"
}

function remove_inv_items {
  ./scripts/inventory-manage.py -f /etc/openstack_deploy/openstack_inventory.json -r "$1"
}

function remove_inv_groups {
  ./scripts/inventory-manage.py -f /etc/openstack_deploy/openstack_inventory.json --remove-group "$1"
}

function run_lock {
  set +e
  run_item="${RUN_TASKS[$1]}"
  file_part="${run_item}"

  # NOTE(sigmavirus24): This handles tasks like:
  # "-e 'rabbitmq_upgrade=true' setup-infrastructure.yml"
  # "/tmp/fix_container_interfaces.yml || true"
  # So we can get the appropriate basename for the upgrade_marker
  for part in $run_item; do
    if [[ "$part" == *.yml ]];then
      file_part="$part"
      break
    fi
  done

  upgrade_marker_file=$(basename ${file_part} .yml)
  upgrade_marker="/etc/openstack_deploy/upgrade-juno/$upgrade_marker_file.complete"

  if [ ! -f "$upgrade_marker" ];then
    # NOTE(sigmavirus24): Use eval so that we properly turn strings like
    # "/tmp/fix_container_interfaces.yml || true"
    # Into a command, otherwise we'll get an error that there's no playbook
    # named ||
    eval "openstack-ansible $2"
    playbook_status="$?"
    echo "ran $run_item"

    if [ "$playbook_status" == "0" ];then
      RUN_TASKS=("${RUN_TASKS[@]/$run_item}")
      touch "$upgrade_marker"
      echo "$run_item has been marked as success"
    else
      echo "******************** FAILURE ********************"
      echo "The upgrade script has failed please rerun the following task to continue"
      echo "Failed on task $run_item"
      echo "Do NOT rerun the upgrade script!"
      echo "Please execute the remaining tasks:"
      # Run the tasks in order
      for item in ${!RUN_TASKS[@]}; do
        echo "${RUN_TASKS[$item]}"
      done
      echo "******************** FAILURE ********************"
      exit 99
    fi
  else
    RUN_TASKS=("${RUN_TASKS[@]/$run_item.*}")
  fi
  set -e
}


## Main ----------------------------------------------------------------------

# Create new openstack_deploy directory.
if [ -d "/etc/rpc_deploy" ];then
  # Create an archive of the old deployment directory
  tar -czf ~/pre-upgrade-backup.tgz /etc/rpc_deploy
  # Move the new deployment directory bits into place
  mkdir -p /etc/openstack_deploy/
  cp -R /etc/rpc_deploy/* /etc/openstack_deploy/
  mv /etc/rpc_deploy /etc/rpc_deploy.OLD
else
  echo "No /etc/rpc_deploy directory found, thus nothing to upgrade."
  exit 1
fi

if [ ! -d "/etc/openstack_deploy/upgrade-juno" ];then
  mkdir -p "/etc/openstack_deploy/upgrade-juno"
fi

# Drop deprecation file.
cat > /etc/rpc_deploy.OLD/DEPRECATED.txt <<EOF
This directory have been deprecated please navigate to "/etc/openstack_deploy"
EOF

# If there is a pip config found remove it
if [ -d "$HOME/.pip" ];then
  tar -czf ~/pre-upgrade-pip-directory.tgz ~/.pip
  rm -rf ~/.pip
fi

# Upgrade ansible in place
./scripts/bootstrap-ansible.sh

# Move the old RPC files to OpenStack files.
pushd /etc/openstack_deploy
  rename 's/rpc_/openstack_/g' rpc_*
popd

# Make the extra configuration directories within the "/etc/openstack_deploy" directory
mkdir -p /etc/openstack_deploy/conf.d
mkdir -p /etc/openstack_deploy/env.d

# Copy over the new environment map
cp etc/openstack_deploy/openstack_environment.yml /etc/openstack_deploy/
cp etc/openstack_deploy/env.d/* /etc/openstack_deploy/env.d/

# Set the rabbitmq cluster name if its not set to something else.
if ! grep '^rabbit_cluster_name\:' /etc/openstack_deploy/user_variables.yml;then
  echo 'rabbit_cluster_name: rpc' | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Add some new variables to user_variables.yml
if ! grep '^galera_innodb_log_file_size' /etc/openstack_deploy/user_variables.yml; then
  echo 'galera_innodb_log_file_size: 128M' | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Set the ssl protocol settings.
echo 'ssl_protocol: "ALL -SSLv2 -SSLv3"' | tee -a /etc/openstack_deploy/user_variables.yml

# Cipher suite string from "https://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/".
echo 'ssl_cipher_suite: "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS"' | tee -a /etc/openstack_deploy/user_variables.yml

# Ensure that the user_group_vars.yml file is not present.
if [ -f "/etc/openstack_deploy/user_group_vars.yml" ];then
    rm /etc/openstack_deploy/user_group_vars.yml
fi
# If OLD ldap bits found in the user_variables file that pertain to ldap upgrade them to the new syntax.
if grep '^keystone_ldap.*' /etc/openstack_deploy/user_variables.yml;then
python <<EOL
import yaml
with open('/etc/openstack_deploy/user_variables.yml', 'r') as f:
    user_vars = yaml.safe_load(f.read())

# Grab a map of the old keystone ldap entries
new_ldap = dict()
for k, v in user_vars.items():
    if k.startswith('keystone_ldap'):
      new_ldap['%s' % k.split('keystone_ldap_')[-1]] = v

# Open user secrets file.
with open('/etc/openstack_deploy/user_secrets.yml', 'r') as fsr:
    user_secrets = yaml.safe_load(fsr.read())

# LDAP variable to instruct keystone to use ldap
ldap = user_secrets['keystone_ldap'] = dict()

# "ldap" section within the keystone_ldap variable.
ldap['ldap'] = new_ldap
with open('/etc/openstack_deploy/user_secrets.yml', 'w') as fsw:
    fsw.write(
        yaml.safe_dump(
            user_secrets,
            default_flow_style=False,
            width=1000
        )
    )
EOL
  # Remove old ldap variables from "user_variables.yml".
  sed -i '/keystone_ldap.*/d' /etc/openstack_deploy/user_variables.yml
fi


# If monitoring as a service or Rackspace cloud variables are present, rewrite them as rpc-extras.yml
if grep -e '^maas_.*' -e '^rackspace_.*' -e '^elasticsearch_.*' -e '^kibana_.*' -e 'logstash_.*' /etc/openstack_deploy/user_variables.yml;then
python <<EOL
import yaml
with open('/etc/openstack_deploy/user_variables.yml', 'r') as f:
    user_vars = yaml.safe_load(f.read())

# Grab a map of the old rpc maas entries
extra_types = ['maas_', 'rackspace_', 'elasticsearch_', 'kibana_', 'logstash_']
rpc_extras = dict()
for k, v in user_vars.items():
    for i in extra_types:
        if k.startswith(i):
          rpc_extras[k] = v

# Clean up rpc extra variables from user variables
for i in rpc_extras.keys():
    del(user_vars[i])

with open('/etc/openstack_deploy/user_variables.yml', 'w') as fsw:
    fsw.write(
        yaml.safe_dump(
            user_vars,
            default_flow_style=False,
            width=1000
        )
    )

with open('/etc/openstack_deploy/user_extras_variables.yml', 'w') as fsw:
    fsw.write(
        yaml.safe_dump(
            rpc_extras,
            default_flow_style=False,
            width=1000
        )
    )
EOL
  # Populate the secrets file with data that should be secret.
  grep -e 'key\:' -e 'token\:' -e 'password\:' -e 'secret\:' /etc/openstack_deploy/user_extras_variables.yml | tee -a /etc/openstack_deploy/user_extras_secrets.yml

  # Remove secrets from the user_variables file that are now in the secrets file.
  sed -i -e '/key\:/d' -e '/token\:/d' -e '/password\:/d' -e '/secret\:/d' /etc/openstack_deploy/user_extras_variables.yml
fi

# Create secrets file.
touch /etc/openstack_deploy/user_secrets.yml

# Populate the secrets file with data that should be secret.
grep -e 'key\:' -e 'token\:' -e 'swift_hash_path' -e 'password\:' -e 'secret\:' /etc/openstack_deploy/user_variables.yml | tee -a /etc/openstack_deploy/user_secrets.yml

# Remove secrets from the user_variables file that are now in the secrets file.
sed -i -e '/key\:/d' -e '/token\:/d' -e '/swift_hash_path/d' -e '/password\:/d' -e '/secret\:/d' /etc/openstack_deploy/user_variables.yml

# Rename the mysql_root_password to galera_root_password.
sed -i 's/mysql_root_password/galera_root_password/g' /etc/openstack_deploy/user_secrets.yml

# Change the glance swift auth value if set. Done because the glance input variable has changed.
if grep '^glance_swift_store_auth_address\:' /etc/openstack_deploy/user_variables.yml | grep -e 'keystone_service_internaluri' -e 'auth_identity_uri'; then
  sed -i 's/^glance_swift_store_auth_address:.*/glance_swift_store_auth_address: "{{ keystone_service_internalurl }}"/g' /etc/openstack_deploy/user_variables.yml
fi

# Create some new secrets.
cat >> /etc/openstack_deploy/user_secrets.yml <<EOF
glance_profiler_hmac_key:
cinder_profiler_hmac_key:
heat_profiler_hmac_key:
nova_v21_service_password:
EOF

# Create the horizon secret key if not found.
if ! grep '^horizon_secret_key\:' /etc/openstack_deploy/user_secrets.yml;then
  echo 'horizon_secret_key:' | tee -a /etc/openstack_deploy/user_secrets.yml
fi

# Regenerate secrets for the new entries
./scripts/pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml

# Preserve any is_metal configurations that differ from new environment layout.
python <<EOL
import os
import yaml

with open('/etc/rpc_deploy.OLD/rpc_environment.yml', 'r') as f:
    rpc_environment = yaml.safe_load(f.read())

for root, _, files in os.walk('/etc/openstack_deploy/env.d'):
    for item in files:
        env_file = os.path.join(root, item)
        with open(env_file, 'r') as f:
            os_environment = yaml.safe_load(f.read())

        if 'container_skel' not in os_environment:
            continue

        changed = False

        for i in os_environment['container_skel']:
            os_item = os_environment['container_skel'][i]

            if i not in rpc_environment['container_skel']:
                continue

            rpc_item = rpc_environment['container_skel'][i]

            if 'is_metal' in rpc_item:
                rpc_metal = rpc_item['is_metal']
            else:
                rpc_metal = False

            if 'is_metal' in os_item['properties']:
                os_metal = os_item['properties']['is_metal']
            else:
                os_metal = False

            if rpc_metal != os_metal:
                changed = True
                os_item['properties']['is_metal'] = rpc_metal

        if changed:
            with open(env_file, 'w') as fsw:
                fsw.write(
                    yaml.safe_dump(
                        os_environment,
                        default_flow_style=False,
                        width=1000
                    )
                )
EOL

# Create the repo servers entries from the same entries found within the infra_hosts group.
if ! grep -R '^repo-infra_hosts\:' /etc/openstack_deploy/user_variables.yml /etc/openstack_deploy/conf.d/;then
  if [ ! -f "/etc/openstack_deploy/conf.d/repo-servers.yml" ];then
python <<EOL
import yaml
with open('/etc/openstack_deploy/openstack_user_config.yml', 'r') as f:
    user_config = yaml.safe_load(f.read())

# Create the new repo servers entries
repo_servers = dict()
o = repo_servers['repo-infra_hosts'] = user_config['infra_hosts']
with open('/etc/openstack_deploy/conf.d/repo-servers.yml', 'w') as fsw:
    fsw.write(
        yaml.safe_dump(
            repo_servers,
            default_flow_style=False,
            width=1000
        )
    )
EOL
  fi
fi

# this is useful for deploys that use an external firewall (that cannot be part of a unified upgrade script)
if ! grep -R '^openstack_repo_url\:' /etc/openstack_deploy/user_* /etc/openstack_deploy/conf.d/; then
  echo -e "openstack_repo_url: \"http://{{ hostvars[groups['pkg_repo'][0]]['ansible_ssh_host'] }}:{{ repo_server_port }}\"" |\
    tee -a /etc/openstack_deploy/user_deleteme_post_upgrade_variables.yml
fi

# Ensure that every pip install action is completed with the '--force-reinstall' argument.
# See https://review.openstack.org/229542 for more details
echo 'pip_install_options: "--force-reinstall"' | tee -a /etc/openstack_deploy/user_deleteme_post_upgrade_variables.yml

sed -i '/^environment_version.*/d' /etc/openstack_deploy/openstack_user_config.yml

# Remove containers that we no longer need
pushd playbooks
  # Ensure that apt-transport-https is installed everywhere before doing anything else,
  # forces True as containers may not exist at this point.
  ansible "hosts:all_containers" \
          -m "apt" \
          -a "update_cache=yes name=apt-transport-https" || true

  # Setup all hosts to run lxc
  openstack-ansible lxc-hosts-setup.yml

  # Ensure the destruction of the containers we don't need.
  ansible hosts \
          -m shell \
          -a 'for i in $(lxc-ls | grep -e "rsyslog" -e "nova_api_ec2" -e "nova_spice_console"); do lxc-destroy -fn $i; done'
  # Clean up post destroy
  openstack-ansible lxc-containers-destroy.yml -e container_group="rsyslog_all"
  openstack-ansible lxc-containers-destroy.yml -e container_group="nova_api_ec2"
  openstack-ansible lxc-containers-destroy.yml -e container_group="nova_spice_console"
popd

# Remove the dead container types from inventory
REMOVED_CONTAINERS=""
REMOVED_CONTAINERS+="$(get_inv_items 'rsyslog_container' | awk '{print $2}') "
REMOVED_CONTAINERS+="$(get_inv_items 'nova_api_ec2' | awk '{print $2}') "
REMOVED_CONTAINERS+="$(get_inv_items 'nova_spice_console' | awk '{print $2}') "
for i in ${REMOVED_CONTAINERS};do
  remove_inv_items $i
done

# Remove unused groups from inventory
REMOVED_GROUPS="nova_api_ec2 nova_api_ec2_container nova_spice_console nova_spice_console_container rabbit rabbit_all"
for i in ${REMOVED_GROUPS}; do
  remove_inv_groups $i
done

# Create a play to fix all networks in all containers on hosts
cat > /tmp/fix_minor_adjustments.yml <<EOF
- name: Fix minor adjustments
  hosts: "horizon_all"
  gather_facts: false
  user: root
  tasks:
    - name: Create the horizon system user
      user:
        name: "{{ horizon_system_user_name }}"
        group: "{{ horizon_system_group_name }}"
        comment: "{{ horizon_system_comment }}"
        shell: "{{ horizon_system_shell }}"
        system: "yes"
        createhome: "yes"
        home: "{{ horizon_system_user_home }}"
    - name: Fix horizon permissions
      command: >
        chown -R "{{ horizon_system_user_name }}":"{{ horizon_system_group_name }}" "/usr/local/lib/python2.7/dist-packages/static"
      register: horizon_cmd_chown
      failed_when: false
      changed_when: horizon_cmd_chown.rc == 0
  vars:
    horizon_system_user_name: "horizon"
    horizon_system_group_name: "www-data"
    horizon_system_shell: "/bin/false"
    horizon_system_comment: "horizon system user"
    horizon_system_user_home: "/var/lib/{{ horizon_system_user_name }}"
- name: Fix keystone things
  hosts: "keystone_all"
  gather_facts: false
  user: root
  tasks:
    - name: Fix keystone permissions
      command: >
        chown -R "keystone":"keystone" "/var/log/keystone"
      register: keystone_cmd_chown
      failed_when: false
      changed_when: keystone_cmd_chown.rc == 0
EOF

# Create a play to fix host things
cat > /tmp/fix_host_things.yml <<EOF
- name: Fix host things
  hosts: "hosts"
  max_fail_percentage: 100
  gather_facts: false
  user: root
  tasks:
    - name: find containers in /var/lib/lxc
      command: "find /var/lib/lxc -maxdepth 2 -type f -name 'config'"
      register: containers
    - name: get the basic container network
      shell: |
        if [ "\$(grep '^lxc.network.name = eth0' {{ item }})" ];then
          grep '^lxc.network.name = eth0' -A1 -B3 {{ item }} | tee {{ item | dirname }}/eth0.ini
          if [ ! "\$(grep '{{ item | dirname }}/eth0.ini' {{ item }})" ];then
            echo 'lxc.include = {{ item | dirname }}/eth0.ini' | tee -a {{ item }}
          fi
        fi
      with_items: containers.stdout_lines
    - name: Remove lxc.network from base config
      lineinfile:
        dest: "{{ item }}"
        state: "absent"
        regexp: "^lxc.network"
      with_items: containers.stdout_lines
    - name: Remove add_network_interface.conf entry
      lineinfile:
        dest: "{{ item }}"
        state: "absent"
        regexp: 'add_network_interface\.conf'
      with_items: containers.stdout_lines
    - name: Remove old add_network_interface.conf file
      file:
        path: "{{ item | dirname }}/add_network_interface.conf"
        state: "absent"
      failed_when: false
      with_items: containers.stdout_lines
    - name: Ensure services log files are fix
      shell: |
        if [ ! -h "/var/log/{{ item }}" ] && [ -d "/var/log/{{ item }}" ];then
          mv /var/log/{{ item }} /openstack/log/{{ inventory_hostname }}-{{ item }}
          ln -s /openstack/log/{{ inventory_hostname }}-{{ item }} /var/log/{{ item }}
        else
          # Exit 99 when nothing found to change
          exit 99
        fi
      failed_when: false
      changed_when: log_change.rc == 0
      register: log_change
      with_items:
        - "cinder"
        - "glance"
        - "heat"
        - "horizon"
        - "keystone"
        - "nova"
        - "neutron"
        - "swift"
EOF

# Create a play for fixing the container networks
# This is cleaning up all old interface files that are from pre kilo.
# The task is set to always succeed because at this point there will be a mix of old
# and new inventory which will have containers that have not been created yet.
cat > /tmp/fix_container_interfaces.yml <<EOF
- name: Fix container things
  hosts: "all_containers"
  max_fail_percentage: 100
  gather_facts: false
  user: root
  tasks:
    - name: Get interface files
      command: ls -1 /etc/network/interfaces.d/
      register: interface_files
      failed_when: false
    - name: Remove old interface files
      file:
        path: "/etc/network/interfaces.d/{{ item }}"
        state: "absent"
      with_items:
        - "{{ interface_files.stdout_lines }}"
      failed_when: false
EOF

# Create a simple task to bounce all networks within a container.
cat > /tmp/ensure_container_networking.yml <<EOF
- name: Ensure container networking is online
  hosts: "all_containers"
  gather_facts: false
  user: root
  tasks:
    - name: Ensure network interfaces are all up
      lxc_container:
        name: "{{ inventory_hostname }}"
        container_command: |
          INTERFACES=""
          INTERFACES+="\$(awk '/auto/ {print \$2}' /etc/network/interfaces) "
          INTERFACES+="\$(ls -1 /etc/network/interfaces.d/ | awk -F'.cfg' '{print \$1}')"
          for i in \${INTERFACES}; do
            ifdown \$i || true
            ifup \$i || true
          done
      delegate_to: "{{ physical_host }}"
EOF

# Create a play to send swift rings to the first swift_host
cat > /tmp/fix_swift_rings_locations.yml <<EOF
- name: Send swift rings from localhost to the first swift node
  hosts: "swift_hosts[0]"
  max_fail_percentage: 100
  gather_facts: false
  user: root
  tasks:
    - name: Ensure the swift system user
      user:
        name: "{{ swift_system_user_name }}"
        group: "{{ swift_system_group_name }}"
        comment: "{{ swift_system_comment }}"
        shell: "{{ swift_system_shell }}"
        system: "yes"
        createhome: "yes"
        home: "{{ swift_system_home_folder }}"
    - name: Ensure "/etc/swift/ring_build_files/" exists
      file:
        path: "{{ item }}"
        owner: "{{ swift_system_user_name }}"
        group: "{{ swift_system_group_name }}"
        state: "directory"
      with_items:
        - "/etc/swift"
        - "/etc/swift/ring_build_files"
    - name: "Copy the rings from localhost to swift_host[0]"
      copy:
        src: "{{ item }}"
        dest: "/etc/swift/ring_build_files/"
        mode: "0644"
        owner: "{{ swift_system_user_name }}"
        group: "{{ swift_system_group_name }}"
      with_fileglob:
        - /etc/swift/rings/*.ring.gz
        - /etc/swift/rings/*.builder
      when: >
        inventory_hostname == groups['swift_hosts'][0]
  vars:
    swift_system_user_name: swift
    swift_system_group_name: swift
    swift_system_shell: /bin/bash
    swift_system_comment: swift system user
    swift_system_home_folder: "/var/lib/{{ swift_system_user_name }}"
EOF

# Create a play to fix juno log-rotate config
cat > /tmp/fix_juno_log_rotate.yml <<EOF
- name: Remove juno log-rotate config
  hosts: "hosts:all_containers"
  gather_facts: false
  user: root
  tasks:
    - name: find log rotate config in /etc/logrotate.d/
      command: "find /etc/logrotate.d -type f -name 'openstack_*'"
      register: log_rotate
    - name: Remove juno log rotate files
      file:
        path: "{{ item }}"
        state: absent
      with_items: log_rotate.stdout_lines
EOF

pushd playbooks
  # Reconfig haproxy if setup.
  if grep '^haproxy_hosts\:' /etc/openstack_deploy/openstack_user_config.yml;then
    # Create the new "galera_monitoring_user" - which now defaults to "monitoring" in mysql
    if ! grep '^galera_monitoring_user:' /etc/openstack_deploy/user_variables.yml; then
      ansible "galera_all[0]" -m "mysql_user" -a "name=monitoring host='%' password='' priv='*.*:USAGE' state=present"
    fi
    ansible haproxy_hosts \
            -m shell \
            -a 'rm /etc/haproxy/conf.d/nova_api_ec2 /etc/haproxy/conf.d/nova_spice_console'
    RUN_TASKS+=("haproxy-install.yml")
  fi

  # Hunt for and remove any rpc_release link files from pip, forces True as
  # containers may not exist at this point.
  ansible "hosts:all_containers" \
          -m "file" \
          -a "path=/root/.pip/links.d/rpc_release.link state=absent" || true

  # The default galera LB monitoring user has changed, we need to clean up the old "haproxy" user.
  if ! grep '^galera_monitoring_user:' /etc/openstack_deploy/user_variables.yml; then
    ansible "galera_all[0]" -m "mysql_user" -a "name=haproxy host='%' password='' priv='*.*:USAGE' state=absent"
    ansible "galera_all[0]" -m "mysql_user" -a "name=haproxy host='localhost' password='' priv='*.*:USAGE' state=absent"
  fi

  # Run the fix adjustments play.
  RUN_TASKS+=("/tmp/fix_minor_adjustments.yml")

  # Run the fix host things play
  RUN_TASKS+=("/tmp/fix_host_things.yml")

  # Run the fix for container networks. Forces True as containers may not exist at this point
  RUN_TASKS+=("/tmp/fix_container_interfaces.yml || true")

  # Run the fix juno log rotate.
  # Forces True as these containers don't exist yet: cinder_scheduler, nova_console, repo, rsyslog
  RUN_TASKS+=("/tmp/fix_juno_log_rotate.yml || true")

  # Send the swift rings to the first swift host if swift was installed in "v10.x".
  if [ "$(ansible 'swift_hosts' --list-hosts)" != "No hosts matched" ] && [ -d "/etc/swift/rings" ];then
    RUN_TASKS+=("/tmp/fix_swift_rings_locations.yml")
  else
    # No swift install found removing the fix file
    rm /tmp/fix_swift_rings_locations.yml
  fi

  # Ensure that the host is setup correctly to support lxc
  RUN_TASKS+=("lxc-hosts-setup.yml")

  # Rerun create containers that will update all running containers with the new bits
  RUN_TASKS+=("lxc-containers-create.yml")

  # Run the container network ensure play
  RUN_TASKS+=("/tmp/ensure_container_networking.yml")

  # With inventory and containers upgraded run the remaining host setup
  RUN_TASKS+=("openstack-hosts-setup.yml")

  # Now run the infrastructure setup
  RUN_TASKS+=("-e 'rabbitmq_upgrade=true' setup-infrastructure.yml")

  # Now upgrade the rest of OpenStack
  RUN_TASKS+=("setup-openstack.yml")

  # Run the tasks in order
  for item in ${!RUN_TASKS[@]}; do
    run_lock $item "${RUN_TASKS[$item]}"
  done
popd
