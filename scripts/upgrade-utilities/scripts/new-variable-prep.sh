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

## Shell Opts ----------------------------------------------------------------
set -e

export MAIN_PATH="${MAIN_PATH:-$(dirname $(dirname $(dirname $(dirname $(readlink -f $0)))))}"
export SCRIPTS_PATH="${SCRIPTS_PATH:-$(dirname $(dirname $(dirname $(readlink -f $0))))}"

# Copy over the new environment map
if [ -f "/etc/openstack_deploy/openstack_environment.yml" ];then
  cp /etc/openstack_deploy/openstack_environment.yml /etc/openstack_deploy/openstack_environment.yml.old
fi
cp ${MAIN_PATH}/etc/openstack_deploy/openstack_environment.yml /etc/openstack_deploy/

for i in $(ls -1 ${MAIN_PATH}/etc/openstack_deploy/env.d/);do
  if [ ! -f "/etc/openstack_deploy/env.d/$i" ];then
    cp "${MAIN_PATH}/etc/openstack_deploy/env.d/$i" /etc/openstack_deploy/env.d/
  fi
done

# Set the rabbitmq cluster name if its not set to something else.
if ! grep '^rabbit_cluster_name\:' /etc/openstack_deploy/user_variables.yml;then
  echo 'rabbit_cluster_name: rpc' | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Add some new variables to user_variables.yml
if ! grep '^galera_innodb_log_file_size' /etc/openstack_deploy/user_variables.yml;then
  echo 'galera_innodb_log_file_size: 128M' | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Add some new variables to user_variables.yml
if ! grep '^galera_cluster_name' /etc/openstack_deploy/user_variables.yml;then
  echo 'galera_cluster_name: rpc_galera_cluster' | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Set the ssl protocol settings.
if ! grep '^ssl_protocol' /etc/openstack_deploy/user_variables.yml;then
  echo 'ssl_protocol: "ALL -SSLv2 -SSLv3"' | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Cipher suite string from "https://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/".
if ! grep '^ssl_cipher_suite' /etc/openstack_deploy/user_variables.yml;then
  echo 'ssl_cipher_suite: "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS"' | tee -a /etc/openstack_deploy/user_variables.yml
fi

# Ensure that the user_group_vars.yml file is not present.
if [ -f "/etc/openstack_deploy/user_group_vars.yml" ];then
    rm /etc/openstack_deploy/user_group_vars.yml
fi

# Create secrets file.
if [ ! -f "/etc/openstack_deploy/user_secrets.yml" ];then
  touch /etc/openstack_deploy/user_secrets.yml
fi

# Make newlines the only separator
IFS=$'\n'

# Populate the secrets file with data that should be secret.
if [ -f "/etc/openstack_deploy/user_extras_variables.yml" ];then
  for i in 'key\:' 'token\:' 'password\:' 'secret\:';do
    for l in $(grep "$i" /etc/openstack_deploy/user_extras_variables.yml);do
      if ! grep "$l" /etc/openstack_deploy/user_extras_secrets.yml;then
        echo "$l" | tee -a /etc/openstack_deploy/user_extras_secrets.yml
      fi
    done
  done

  if [ -f "/etc/openstack_deploy/user_extras_secrets.yml" ];then
    # Setting the secret generator to always return true because the file may be a zero byte file
    ${SCRIPTS_PATH}/pw-token-gen.py --file /etc/openstack_deploy/user_extras_secrets.yml || true
  fi
fi

for i in 'key\:' 'token\:' 'swift_hash_path' 'password\:' 'secret\:';do
  for l in $(grep "$i" /etc/openstack_deploy/user_variables.yml);do
    if ! grep "$l" /etc/openstack_deploy/user_secrets.yml; then
      echo "$l" | tee -a /etc/openstack_deploy/user_secrets.yml
    fi
  done
done

# Rename the mysql_root_password to galera_root_password.
sed -i 's/mysql_root_password/galera_root_password/g' /etc/openstack_deploy/user_secrets.yml

# Change the glance swift auth value if set. Done because the glance input variable has changed.
if grep '^glance_swift_store_auth_address\:' /etc/openstack_deploy/user_variables.yml | grep -e 'keystone_service_internaluri' -e 'auth_identity_uri'; then
  sed -i 's/^glance_swift_store_auth_address:.*/glance_swift_store_auth_address: "{{ keystone_service_internalurl }}"/g' /etc/openstack_deploy/user_variables.yml
fi

# Create some new secrets.
for i in 'glance_profiler_hmac_key:' 'cinder_profiler_hmac_key:' 'heat_profiler_hmac_key:' 'nova_v21_service_password:';do
  if ! grep "^$i" /etc/openstack_deploy/user_secrets.yml;then
    echo "$i" | tee -a /etc/openstack_deploy/user_secrets.yml
  fi
done

# Create the horizon secret key if not found.
if ! grep '^horizon_secret_key\:' /etc/openstack_deploy/user_secrets.yml;then
  echo 'horizon_secret_key:' | tee -a /etc/openstack_deploy/user_secrets.yml
fi

# this is useful for deploys that use an external firewall (that cannot be part of a unified upgrade script)
if ! grep -R '^openstack_repo_url\:' /etc/openstack_deploy/user_* /etc/openstack_deploy/conf.d/; then
  echo -e "openstack_repo_url: \"http://{{ hostvars[groups['pkg_repo'][0]]['ansible_ssh_host'] }}:{{ repo_server_port }}\"" |\
    tee -a /etc/openstack_deploy/user_deleteme_post_upgrade_variables.yml
fi

# Set the galera monitoring user to the old Juno Value.
if ! grep '^galera_monitoring_user' /etc/openstack_deploy/user_deleteme_post_upgrade_variables.yml;then
  echo 'galera_monitoring_user: "haproxy"' | tee -a /etc/openstack_deploy/user_deleteme_post_upgrade_variables.yml
fi

# Regenerate secrets for the new entries if any
${SCRIPTS_PATH}/pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml
