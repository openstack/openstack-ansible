.. _manual-upgrade:

Manual upgrade steps
====================

The steps detailed here match those performed by the ``run-upgrade.sh``
script. Any of these steps can be run safely multiple times.

Check out the Liberty release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure your OpenStack-Ansible code is on a Liberty release of 12.0.8 or later.

.. note::

   Versions before 12.0.8 do not include the upgrade capability.

.. code-block:: console

   # git checkout 12.0.8

Preparing the shell variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    This step is optional, since the environment variables are
    shortcuts. Files can be referenced directly.

From the ``openstack-ansible`` root directory, run the following commands:

.. code-block:: console

   # export MAIN_PATH="$(pwd)"
   # export SCRIPTS_PATH="${MAIN_PATH}/scripts"
   # export UPGRADE_PLAYBOOKS="${SCRIPTS_PATH}/upgrade-utilities/playbooks"

These variables reduce typing when running the remaining upgrade
tasks.

Re-bootstrap OpenStack-Ansible for Liberty
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bootstrapping OpenStack-Ansible again ensures that new external OpenStack-Ansible role
dependencies are in place before the Liberty version of playbooks and roles
run.

.. code-block:: console

   # ${SCRIPTS_PATH}/bootstrap-ansible.sh

Temporarily disabling the security hardening role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To avoid issues and ease troubleshooting, if an issue
appears during the upgrade, disable the security hardening role
before running the following steps. Set the
variable ``apply_security_hardening`` to False:

.. code-block:: console

   # echo 'apply_security_hardening: False' >> /etc/openstack_deploy/user_zzz_disable_security_hardening.yml

Change to playbooks directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change to the playbooks directory the OpenStack-Ansible dynamic
inventory is found automatically.

.. code-block:: console

   # cd playbooks

Update configuration and environment files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user configuration files in ``/etc/openstack_deploy/`` and the environment
layout in ``/etc/openstack_deploy/env.d`` have new names and
values added in Liberty.

See :ref:`config-change-playbook` for more details.

.. code-block:: console

   # openstack-ansible "${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml"

Update user secrets file
~~~~~~~~~~~~~~~~~~~~~~~~

Liberty introduces new user secrets to the stack (for example, in aodh).
These are populated automatically with the following playbook.

See :ref:`user-secrets-playbook` for more details.

.. code-block:: console

   # openstack-ansible "${UPGRADE_PLAYBOOKS}/user-secrets-adjustment.yml"

Upgrade hosts
~~~~~~~~~~~~~

Before installing the infrastructure and OpenStack, update the host machines.

.. code-block:: console

   # openstack-ansible setup-hosts.yml --limit '!galera_all[0]'

This command is the same as doing host setups on a new install. The first
member of the ``galera_all`` host group is excluded to prevent simultaneous
restarts of all Galera containers.

Update Galera LXC container configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the first Galera container's configuration independently.

.. code-block:: console

   # openstack-ansible lxc-containers-create.yml --limit galera_all[0]

This command is a subset of the host setup playbook, limited to the first
member of the ``galera_all`` host group so that its container is restarted only
after other Galera containers have been restarted.

Cleanup ``pip.conf`` file in the ``repo_servers``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a ``pip.conf`` file exists within the repository server infrastructure,
it can cause build failures when upgrading to Liberty.
This play removes the ``pip.conf`` file from the repository
servers.

See :ref:`repo-server-pip-conf-removal` for more details.

.. code-block:: console

   # openstack-ansible "${UPGRADE_PLAYBOOKS}/repo-server-pip-conf-removal.yml"


Upgrade infrastructure
~~~~~~~~~~~~~~~~~~~~~~

Running the standard OpenStack-Ansible infrastructure playbook applies the
relevant Liberty settings and packages. However, MariaDB and Galera require an
extra option to specify an upgrade from the 5.5 series to 10.0. This upgrade
is required for the Liberty release of OpenStack-Ansible.

For certain versions of Kilo, you must upgrade the RabbitMQ minor version.

See :ref:`setup-infra-playbook` for details.

.. code-block:: console

   # openstack-ansible setup-infrastructure.yml -e 'galera_upgrade=true' \
   -e 'rabbitmq_upgrade=true'


Disable neutron port security driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the playbook ``disable-neutron-port-security.yml`` to disable the neutron
port security extension if there is no existing override.

See :ref:`neutron-port-sec-playbook` for details.

.. code-block:: console

   # openstack-ansible "${UPGRADE_PLAYBOOKS}/disable-neutron-port-security.yml"

Upgrade OpenStack
~~~~~~~~~~~~~~~~~

Upgrade the OpenStack components with the installation playbook,
without any additional options.

.. code-block:: console

   # openstack-ansible setup-openstack.yml

Clean up RabbitMQ
~~~~~~~~~~~~~~~~~

Use the ``cleanup-rabbitmq-vhost.yml`` playbook to remove residual virtual
hosts and users that are replaced in Liberty.

See :ref:`cleanup-rabbit-playbook` for details.

.. code-block:: console

   # openstack-ansible "${UPGRADE_PLAYBOOKS}/cleanup-rabbitmq-vhost.yml \
   -e 'pip_install_options=--force-reinstall'"

Removing the security hardening prevention variable file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can now return the security hardening to its former value by
removing the file previously created:

.. code-block:: console

   # rm /etc/openstack_deploy/user_zzz_disable_security_hardening.yml

--------------

.. include:: navigation.txt
