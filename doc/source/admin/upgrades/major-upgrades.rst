==============
Major upgrades
==============

This guide provides information about the upgrade process from
|previous_release_formal_name| to |current_release_formal_name|
for OpenStack-Ansible.

.. note::

   You can only upgrade between sequential releases.

Introduction
============

For upgrades between major versions, the OpenStack-Ansible repository provides
playbooks and scripts to upgrade an environment. The ``run-upgrade.sh``
script runs each upgrade playbook in the correct order, or playbooks can be run
individually if necessary. Alternatively, a deployer can upgrade manually.

For more information about the major upgrade process, see
:ref:`upgrading-by-using-a-script` and :ref:`upgrading-manually`.

.. warning::

   |upgrade_warning| Test this on a development environment first.

.. _upgrading-by-using-a-script:

Upgrading by using a script
===========================

The |current_release_formal_name| release series of OpenStack-Ansible contains
the code for migrating from |previous_release_formal_name| to
|current_release_formal_name|.

Running the upgrade script
~~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade from |previous_release_formal_name| to |current_release_formal_name|
by using the upgrade script, perform the following steps in the
``openstack-ansible`` directory:

#. Change directory to the repository clone root directory:

   .. code-block:: console

      # cd /opt/openstack-ansible

#. Run the following commands:

   .. parsed-literal::

      # git checkout |latest_tag|
      # ./scripts/run-upgrade.sh

For more information about the steps performed by the script, see
:ref:`upgrading-manually`.

.. _upgrading-manually:

Upgrading manually
==================

Manual upgrades are useful for scoping the changes in the upgrade process
(for example, in very large deployments with strict SLA requirements), or
performing other upgrade automation beyond that provided by OpenStack-Ansible.

The steps detailed here match those performed by the ``run-upgrade.sh``
script. You can safely run these steps multiple times.

Preflight checks
~~~~~~~~~~~~~~~~

Before starting with the upgrade, perform preflight health checks to ensure
your environment is stable. If any of those checks fail, ensure that the issue
is resolved before continuing.

Check out the |current_release_formal_name| release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure that your OpenStack-Ansible code is on the latest
|current_release_formal_name| tagged release.

.. parsed-literal::

    # git checkout |latest_tag|

Prepare the shell variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define these variables to reduce typing when running the remaining upgrade
tasks. Because these environments variables are shortcuts, this step is
optional. If you prefer, you can reference the files directly during the
upgrade.

.. code-block:: console

    # cd /opt/openstack-ansible
    # export MAIN_PATH="$(pwd)"
    # export SCRIPTS_PATH="${MAIN_PATH}/scripts"

Backup the existing OpenStack-Ansible configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make a backup of the configuration of the environment:

.. parsed-literal::

    # source_series_backup_file="/openstack/backup-openstack-ansible-|previous_series_name|.tar.gz"
    # tar zcf ${source_series_backup_file} /etc/openstack_deploy /etc/ansible/ /usr/local/bin/openstack-ansible.rc

Bootstrap the new Ansible and OSA roles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To ensure that there is no currently set ANSIBLE_INVENTORY to override
the default inventory location, we unset the environment variable.

.. code-block:: console

    # unset ANSIBLE_INVENTORY

Bootstrap Ansible again to ensure that all OpenStack-Ansible role
dependencies are in place before you run playbooks from the
|current_release_formal_name| release.

.. code-block:: console

    # ${SCRIPTS_PATH}/bootstrap-ansible.sh

Change to the playbooks directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change to the playbooks directory to simplify the CLI commands from here on
in the procedure, given that most playbooks executed are in this directory.

.. code-block:: console

    # cd playbooks

Implement changes to OSA configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If there have been any OSA variable name changes or environment/inventory
changes, there is a playbook to handle those changes to ensure service
continuity in the environment when the new playbooks run. The playbook is
tagged to ensure that any part of it can be executed on its own or skipped.
Please review the contents of the playbook for more information.

.. code-block:: console

    # openstack-ansible "${SCRIPTS_PATH}/upgrade-utilities/deploy-config-changes.yml"

Upgrade hosts
~~~~~~~~~~~~~

Before installing the infrastructure and OpenStack, update the host machines.

With the introduction of the PKI ansible role, OSA now manages its own Certificate
Authority (CA) when self-signed certificates are used. Before proceeding
with the upgrade, you will need to override ``openstack_pki_authorities``
and ``openstack_pki_service_intermediate_cert_name`` in your user_variables.
Otherwise, sample authorities will be generated for root and intermediate
certificates and all self-signed certificates generated later will be
signed with them.

.. warning::

    Usage of non-trusted certificates for RabbitMQ is not possible
    due to requirements of newer ``amqp`` versions.

To generate new CA, you will need to run the following command:

.. code-block:: console

    # openstack-ansible certificate-authority.yml

Once CA is generated, we can proceed with standard OpenStack upgrade steps:

.. code-block:: console

    # openstack-ansible setup-hosts.yml --limit '!galera_all:!rabbitmq_all' -e package_state=latest

This command is the same setting up hosts on a new installation. The
``galera_all`` and ``rabbitmq_all`` host groups are excluded to prevent
reconfiguration and restarting of any of those containers as they need to
be updated, but not restarted.

Once that is complete, upgrade the final host groups with the flag to prevent
container restarts.

.. code-block:: console

    # openstack-ansible setup-hosts.yml -e 'lxc_container_allow_restarts=false' --limit 'galera_all:rabbitmq_all'

Upgrade infrastructure
~~~~~~~~~~~~~~~~~~~~~~

We can now go ahead with the upgrade of all the infrastructure components. To
ensure that rabbitmq and mariadb are upgraded, we pass the appropriate flags.

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'galera_upgrade=true' -e 'rabbitmq_upgrade=true' -e package_state=latest

With this complete, we can now restart the mariadb containers one at a time,
ensuring that each is started, responding, and synchronized with the other
nodes in the cluster before moving on to the next steps. This step allows
the LXC container configuration that you applied earlier to take effect,
ensuring that the containers are restarted in a controlled fashion.

.. code-block:: console

    # openstack-ansible "${SCRIPTS_PATH}/upgrade-utilities/galera-cluster-rolling-restart.yml"

Upgrade OpenStack
~~~~~~~~~~~~~~~~~

We can now go ahead with the upgrade of all the OpenStack components.

.. code-block:: console

    # openstack-ansible setup-openstack.yml -e package_state=latest
