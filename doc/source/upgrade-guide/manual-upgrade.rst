.. _manual-upgrade:

Manual Upgrade Steps
====================

The steps detailed here match those performed by the ``run-upgrade.sh``
script. Any of these steps can safely be run multiple times.

Checkout Liberty version
------------------------

Ensure your OpenStack-Ansible code is on a Liberty release of 12.0.8 or later.

Versions prior to this did not include the upgrade utilities.

.. code-block:: console

    # git checkout 12.0.8

Preparing the shell variables
-----------------------------

.. note::

    This is step is optional, since these environment variables are simply
    shortcuts. Files can be referenced directly.

From the ``openstack-ansible`` root directory, run the following.

.. code-block:: console

    # export MAIN_PATH="$(pwd)"
    # export SCRIPTS_PATH="${MAIN_PATH}/scripts"
    # export UPGRADE_PLAYBOOKS="${SCRIPTS_PATH}/upgrade_utilities/playbooks"

These variables will reduce typing when running the remaining upgrade
tasks.

Re-bootstrap Ansible for Liberty
-------------------------------

Bootstrapping Ansible again ensures that new external Ansible role
dependencies are in place before the Liberty version of playbooks and roles
run.

.. code-block:: console

    # ${SCRIPTS_PATH}/bootstrap-ansible.sh

Change to playbooks directory
-----------------------------

Move to the playbooks directory so that the Ansible dynamic
inventory will be found automatically

.. code-block:: console

    # cd playbooks

Update configuration and environment files
------------------------------------------

The user configuration files in ``/etc/openstack_deploy/`` and the environment
layout in ``/etc/openstack_deploy/env.d`` have had names changed and new
values added in Liberty. This step updates the files as necessary.

See :ref:`config-change-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml

.. note::

    The `-e pip_install_options=--force-reinstall` ensures that all pip
    packages are reinstalled and running the correct version on hosts.

Update user secrets file
------------------------

Liberty introduces new user secrets to the stack (for example, in aodh).
These are populated automatically with the following playbook.

See :ref:`user-secrets-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/user-secrets-adjustments.yml

Upgrade hosts
-------------

Before installing the infrastructure and OpenStack, update the host machines.

.. code-block:: console

    # openstack-ansible setup-hosts.yml

This command is the same as doing host setups on a new install.

Cleanup pip.conf file in the repo_servers if found
--------------------------------------------------

It is possible that a ``pip.conf`` file may exist within the repository server
infrastructure. If this file exists it will cause build failures when upgrading
to Liberty. This play will remove the ``pip.conf`` file from the repository
servers if it's found.

See :ref:`repo-server-pip-conf-removal` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/repo-server-pip-conf-removal.yml


Upgrade infrastructure
----------------------

Running the standard OpenStack-Ansible infrastructure playbook applies the
relevant Liberty settings and packages. However, MariaDB/Galera needs an
extra option to specify an upgrade from the 5.5 series to 10.0. This upgrade
is required for the Liberty release of OpenStack-Ansible.

RabbitMQ may need a minor version upgrade depending on what version of Kilo
was previously installed.

See :ref:`setup-infra-playbook` for details.

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'galera_upgrade=true' \
    -e 'rabbitmq_upgrade=true'


Disable Neutron port security driver
------------------------------------

Use the playbook ``disable-neutron-port-security.yml`` to disable the Neutron
port security extension if there is no existing override.

See :ref:`neutron-port-sec-playbook` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/disable-neutron-port-security.yml

Upgrade OpenStack
-----------------

Upgrading the OpenStack components is done with the same playbook that
installs them, without any additional options.

.. code-block:: console

    # openstack-ansible setup-openstack.yml

Clean up RabbitMQ
-----------------

Use the ``cleanup-rabbitmq-vhost.yml`` playbook to remove residual virtual
hosts and users that are replaced in Liberty.

See :ref:`cleanup-rabbit-playbook` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/cleanup-rabbitmq-vhost.yml \
    -e 'pip_install_options=--force-reinstall'"

--------------

.. include:: navigation.txt
