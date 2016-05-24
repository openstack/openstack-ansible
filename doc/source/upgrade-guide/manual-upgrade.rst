.. _manual-upgrade:

Manual Upgrade Steps
====================

The steps detailed here match those performed by the ``run-upgrade.sh``
script. Any of these steps can safely be run multiple times.

Checkout Newton version
-----------------------

Ensure your OpenStack-Ansible code is on the latest Newton release tag (14.x.x).

.. code-block:: console

    # git checkout stable/newton
    # LATEST_TAG=$(git describe --abbrev=0 --tags)
    # git checkout ${LATEST_TAG}

Preparing the shell variables
-----------------------------

.. note::

    This step is optional, since these environment variables are simply
    shortcuts. Files can be referenced directly.

From the ``openstack-ansible`` root directory, run the following.

.. code-block:: console

    # export MAIN_PATH="$(pwd)"
    # export SCRIPTS_PATH="${MAIN_PATH}/scripts"
    # export UPGRADE_PLAYBOOKS="${SCRIPTS_PATH}/upgrade-utilities/playbooks"

These variables will reduce typing when running the remaining upgrade
tasks.

Re-bootstrap Ansible for Newton
-------------------------------

Bootstrapping Ansible again ensures that new external Ansible role
dependencies are in place before running playbooks from the Newton
release.

.. code-block:: console

    # ${SCRIPTS_PATH}/bootstrap-ansible.sh

Change to playbooks directory
-----------------------------

Change to the playbooks directory so that the Ansible dynamic
inventory will be found automatically.

.. code-block:: console

    # cd playbooks

Update configuration and environment files
------------------------------------------

The user configuration files in ``/etc/openstack_deploy/`` and the environment
layout in ``/etc/openstack_deploy/env.d`` have had names changed and new
values added in Newton. This step updates the files as necessary.

See :ref:`config-change-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml"

.. note::

    The `-e pip_install_options=--force-reinstall` ensures that all pip
    packages are reinstalled and running the correct version on hosts.

Update user secrets file
------------------------

Newton introduces new user secrets to the stack. These are populated
automatically with the following playbook.

See :ref:`user-secrets-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/user-secrets-adjustment.yml"

Upgrade hosts
-------------

Before installing the infrastructure and OpenStack, update the host machines.

.. code-block:: console

    # openstack-ansible setup-hosts.yml --limit '!galera_all[0]'

This command is the same as doing host setups on a new install. The first
member of the ``galera_all`` host group is excluded to prevent simultaneous
restarts of all galera containers.

Update Galera LXC container configuration
-----------------------------------------

Update the first galera container's configuration independently.

.. code-block:: console

    # openstack-ansible lxc-containers-create.yml --limit galera_all[0]

This command is a subset of the host setup playbook, limited to the first
member of the ``galera_all`` host group so that its container is restarted only
after other galera containers have been restarted in the previous step.

Cleanup ``pip.conf`` file in the ``repo_servers``
-------------------------------------------------

It is possible that a ``pip.conf`` file may exist within the repository server
infrastructure. If this file exists, it will cause build failures when upgrading
to Newton. This play will remove the ``pip.conf`` file from the repository
servers if it is found.

See :ref:`repo-server-pip-conf-removal` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/repo-server-pip-conf-removal.yml"


Upgrade infrastructure
----------------------

Running the standard OpenStack-Ansible infrastructure playbook applies the
relevant Newton settings and packages. This upgrade is required for the Newton
release of OpenStack-Ansible.

RabbitMQ may need a minor version upgrade depending on what version of Mitaka
was previously installed.

See :ref:`setup-infra-playbook` for details.

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'galera_upgrade=true' \
    -e 'rabbitmq_upgrade=true'

Upgrade OpenStack
-----------------

Upgrading the OpenStack components is done with the same playbook that
installs them, without any additional options.

.. code-block:: console

    # openstack-ansible setup-openstack.yml

--------------

.. include:: navigation.txt
