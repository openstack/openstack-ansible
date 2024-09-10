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

# tempest and testr options, default is to run tempest in serial
export TESTR_OPTS=${TESTR_OPTS:-''}

# Disable the python output buffering so that jenkins gets the output properly
export PYTHONUNBUFFERED=1

# Extra options to pass to the AIO bootstrap process
export BOOTSTRAP_OPTS=${BOOTSTRAP_OPTS:-''}

# Ensure the terminal type is set
export TERM=linux

# Store the clone repo root location
export OSA_CLONE_DIR="$(readlink -f $(dirname ${0})/..)"

# The directory in which the ansible logs will be placed
export ANSIBLE_LOG_DIR="/openstack/log/ansible-logging"

# Set the scenario to execute based on the first CLI parameter
export SCENARIO=${1:-"aio_lxc"}

# Set the action base on the second CLI parameter
# Actions available: [ 'deploy', 'upgrade', 'varstest', 'shastest', 'linters' ]
export ACTION=${2:-"deploy"}

# Set the installation method for the OpenStack services
export INSTALL_METHOD=${3:-"source"}

# enable the ARA callback plugin
export SETUP_ARA=${SETUP_ARA:-true}

# List of scenarios that update configuration files prior to the upgrade
export SCENARIOS_WITH_CONFIG_UPDATE=("tls")

## Change branch for Upgrades ------------------------------------------------
# If the action is to upgrade, then store the current SHA,
# checkout the source SHA before executing the greenfield
# deployment.
# This needs to be done before the first "source" to ensure
# the correct functions are used for the branch.
if [[ "${ACTION}" =~ "upgrade" ]]; then
    # Set the source branch for upgrade tests
    # Be sure to change this whenever a new stable branch
    # is created.
    # The branch prefix will also change from 'stable/' to 'unmaintained/'
    # in the future, so determine the branch prefix dynamically
    UPGRADE_ACTION_ARRAY=(${ACTION//_/ })
    export UPGRADE_SOURCE_RELEASE=${UPGRADE_ACTION_ARRAY[1]:-'2024.1'}
    export UPGRADE_SOURCE_BRANCH_PREFIX=$(git branch -r --list 'origin/*' | grep $UPGRADE_SOURCE_RELEASE | sort | tail -n 1 | cut -d '/' -f 2)
    export UPGRADE_SOURCE_BRANCH=${UPGRADE_SOURCE_BRANCH:-$UPGRADE_SOURCE_BRANCH_PREFIX/$UPGRADE_SOURCE_RELEASE}

    # Store the target SHA/branch
    export UPGRADE_TARGET_BRANCH=$(git rev-parse HEAD)
    export OPENSTACK_SETUP_EXTRA_ARGS="-e tempest_install=no -e tempest_run=no -e rally_install=no"
    export ANSIBLE_GATHER_SUBSET="network,hardware,virtual"

    # Now checkout the source SHA/branch
    git checkout ${UPGRADE_SOURCE_BRANCH}

    unset SKIP_OSA_RUNTIME_VENV_BUILD
    unset SKIP_OSA_BOOTSTRAP_AIO
    unset SKIP_OSA_ROLE_CLONE
fi

## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source "${OSA_CLONE_DIR}/scripts/scripts-library.sh"

## Main ----------------------------------------------------------------------
# Log some data about the instance and the rest of the system
gate_log_requirements

log_instance_info

run_dstat || true

load_nodepool_pip_opts

# Bootstrap Ansible
if [[ -z "${SKIP_OSA_BOOTSTRAP_AIO+defined}" ]]; then
  source "${OSA_CLONE_DIR}/scripts/bootstrap-ansible.sh"
fi

# Flush all the iptables rules set by openstack-infra
if command -v iptables; then
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

# Bootstrap an AIO
if [[ -z "${SKIP_OSA_BOOTSTRAP_AIO+defined}" && "${ACTION}" != "linters" &&  "${ACTION}" != "shastest" ]]; then
    source "${OSA_CLONE_DIR}/scripts/bootstrap-aio.sh"
fi

if [[ "${ACTION}" == "varstest" ]]; then
  pushd "${OSA_CLONE_DIR}/tests"
      openstack-ansible test-vars-overrides.yml
  popd
elif [[ "${ACTION}" == "shastest" ]]; then
  pushd "${OSA_CLONE_DIR}/tests"
      openstack-ansible test-upstream-shas.yml
  popd
elif [[ "${ACTION}" == "linters" ]]; then
  pushd "${OSA_CLONE_DIR}"
    # Install linter tools
    ${PIP_COMMAND} install --isolated ${PIP_OPTS} -r ${OSA_CLONE_DIR}/test-requirements.txt
    # Disable Ansible color output
    export ANSIBLE_NOCOLOR=1
    # Create ansible logging directory
    mkdir -p ${ANSIBLE_LOG_DIR}

    # Prepare the hosts
    export ANSIBLE_LOG_PATH="${ANSIBLE_LOG_DIR}/ansible-syntax-check.log"

    # defining working directories
    VENV_BIN_DIR=$(dirname ${PIP_COMMAND})

    source /usr/local/bin/openstack-ansible.rc
    # Check if we have test playbook and running checks
    if [[ -f "/etc/ansible/roles/${SCENARIO}/examples/playbook.yml" ]]; then
      ROLE_DIR="/etc/ansible/roles/${SCENARIO}"
      ${VENV_BIN_DIR}/ansible-lint ${ROLE_DIR}/examples/playbook.yml -c ${OSA_CLONE_DIR}/.ansible-lint
      ansible-playbook --syntax-check --list-tasks ${ROLE_DIR}/examples/playbook.yml
    # If we don't have test playbook we assume that we're testing integrated repo
    else
      ROLE_DIR="${OSA_CLONE_DIR}"
      ${VENV_BIN_DIR}/ansible-lint playbooks/ --exclude /etc/ansible/roles
      ansible-playbook --syntax-check --list-tasks playbooks/setup-everything.yml
    fi

    # Run bashate
    grep --recursive --binary-files=without-match \
      --files-with-match '^.!.*\(ba\)\?sh$' \
      --exclude-dir .tox \
      --exclude-dir .git \
      "${ROLE_DIR}" | xargs -r -n1 ${VENV_BIN_DIR}/bashate --error . --verbose --ignore=E003,E006,E040

    # Run pep8 check
    grep --recursive --binary-files=without-match \
      --files-with-match '^.!.*python$' \
      --exclude-dir .eggs \
      --exclude-dir .git \
      --exclude-dir .tox \
      --exclude-dir *.egg-info \
      --exclude-dir doc \
      "${ROLE_DIR}" | xargs -r ${VENV_BIN_DIR}/flake8 --verbose

  popd
else
  pushd "${OSA_CLONE_DIR}/playbooks"
    # Disable Ansible color output
    export ANSIBLE_NOCOLOR=1
    export ANSIBLE_GATHER_SUBSET="${ANSIBLE_GATHER_SUBSET:-!all,min}"

    # Create ansible logging directory
    mkdir -p ${ANSIBLE_LOG_DIR}

    # Log some data about the instance and the rest of the system
    log_instance_info

    # First we gather facts about the hosts to populate the fact cache.
    # We can't gather the facts for all hosts yet because the containers
    # aren't built yet.
    ansible -m setup -a "gather_subset=${ANSIBLE_GATHER_SUBSET}" hosts 2>${ANSIBLE_LOG_DIR}/facts-hosts.log

    # Prepare the hosts
    export ANSIBLE_LOG_PATH="${ANSIBLE_LOG_DIR}/setup-hosts.log"
    openstack-ansible setup-hosts.yml -e osa_gather_facts=False

    # Log some data about the instance and the rest of the system
    log_instance_info

    if [[ $SCENARIO =~ "hosts" ]]; then
      # Verify our hosts setup and do not continue with openstack/infra part
      openstack-ansible healthcheck-hosts.yml -e osa_gather_facts=False
      exit $?
    fi

    # Reload environment file and apply variables for the session
    set -a
    . /etc/environment
    set +a

    # Once setup-hosts is complete, we should gather facts for everything
    # (now including containers) so that the fact cache is complete for the
    # remainder of the run.
    ansible -m setup -a "gather_subset=${ANSIBLE_GATHER_SUBSET}" all 1>${ANSIBLE_LOG_DIR}/facts-all.log

    # Prepare the infrastructure
    export ANSIBLE_LOG_PATH="${ANSIBLE_LOG_DIR}/setup-infrastructure.log"
    openstack-ansible setup-infrastructure.yml -e osa_gather_facts=False

    # Log some data about the instance and the rest of the system
    log_instance_info

    if [[ $SCENARIO =~ "infra" && ! $ACTION =~ "upgrade"  ]]; then
      # Verify our infra setup and do not continue with openstack part
      openstack-ansible healthcheck-infrastructure.yml -e osa_gather_facts=False
    fi

    # Setup OpenStack
    export ANSIBLE_LOG_PATH="${ANSIBLE_LOG_DIR}/setup-openstack.log"
    openstack-ansible setup-openstack.yml -e osa_gather_facts=False ${OPENSTACK_SETUP_EXTRA_ARGS:-}

    # Log some data about the instance and the rest of the system
    log_instance_info

  popd
fi

# If the action is to upgrade, then checkout the original SHA for
# the checkout, and execute the upgrade.
if [[ "${ACTION}" =~ "upgrade" ]]; then

    # Checkout the original HEAD we started with
    git checkout ${UPGRADE_TARGET_BRANCH}

    # Unset environment variables used by the bootstrap-ansible
    # script to allow newer versions of Ansible and global
    # requirements to be installed.
    unset ANSIBLE_PACKAGE
    unset TOX_CONSTRAINTS_FILE
    unset PIP_OPTS
    unset UPGRADE_TARGET_BRANCH

    load_nodepool_pip_opts

    # Source the current scripts-library.sh functions
    source "${OSA_CLONE_DIR}/scripts/scripts-library.sh"
    # We need this as in stein we were deploying custom
    # /etc/openstack_deploy/env.d/aio_metal.yml for metal installs
    export SKIP_CUSTOM_ENVD_CHECK=true
    export DROP_ROLE_DIRS=true

    # Export ZUUL_SRC_PATH only when integrated repo folder exists. Based on that
    # we make an assumption about if we're in CI or not
    if [[ -d "/home/zuul/src/opendev.org/openstack/openstack-ansible" ]]; then
      export ZUUL_SRC_PATH="/home/zuul/src"
      # Doing symlinking here, as bootstrap role won't be called
      ln -s $ZUUL_SRC_PATH /openstack/src
    fi
    # Update AIO config files for certain scenarios
    for item in "${SCENARIOS_WITH_CONFIG_UPDATE[@]}"; do
      if [[ "${SCENARIO}" =~ "${item}" ]]; then
        export BOOTSTRAP_EXTRA_PARAMS="${BOOTSTRAP_EXTRA_PARAMS:-} -t prepare-aio-config"
        "${OSA_CLONE_DIR}/scripts/bootstrap-aio.sh"
        break
      fi
    done
    # To execute the upgrade script we need to provide
    # an affirmative response to the warning that the
    # upgrade is irreversable.
    echo 'YES' | SOURCE_SERIES=${UPGRADE_SOURCE_RELEASE} bash "${OSA_CLONE_DIR}/scripts/run-upgrade.sh"

    if [[ $SCENARIO =~ "infra" ]]; then
      # TODO(noonedeadpunk): Remove after Y release
      set -a
      . ${OSA_CLONE_DIR}/scripts/upgrade-utilities/unset-ansible-env.rc
      set +a
      # Verify our infra setup after upgrade
      openstack-ansible ${OSA_CLONE_DIR}/playbooks/healthcheck-infrastructure.yml -e osa_gather_facts=False
    fi

fi

exit_success
