.. _manual-upgrade:

===============
Manual upgrades
===============

Deployers can run the upgrade steps manually. Manual execution is useful for
scoping the changes in the upgrade process (For example, in very large
deployments with strict SLA requirements), or for inclusion into other
orchestration for upgrade automation beyond what OpenStack-Ansible provides.

The steps detailed here match those performed by the ``run-upgrade.sh``
script. Any of these steps can safely be run multiple times.

Check out the Newton release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure your OpenStack-Ansible code is on the latest Newton release tag (14.x.x).

.. code-block:: console

    # git checkout stable/newton
    # LATEST_TAG=$(git describe --abbrev=0 --tags)
    # git checkout ${LATEST_TAG}

Prepare the shell variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    This step is optional, since these environment variables are simply
    shortcuts. Files can be referenced directly.

From the ``openstack-ansible`` root directory, run the following commands:

.. code-block:: console

    # export MAIN_PATH="$(pwd)"
    # export SCRIPTS_PATH="${MAIN_PATH}/scripts"
    # export UPGRADE_PLAYBOOKS="${SCRIPTS_PATH}/upgrade-utilities/playbooks"

These variables reduce typing when running the remaining upgrade
tasks.

Re-bootstrap Ansible for Newton
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bootstrapping Ansible again ensures that all OpenStack-Ansible role
dependencies are in place before running playbooks from the Newton
release.

.. code-block:: console

    # ${SCRIPTS_PATH}/bootstrap-ansible.sh

Change to playbooks directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change to the playbooks directory so that the OpenStack-Ansible dynamic
inventory is found automatically.

.. code-block:: console

    # cd playbooks

Pre-flight checks
~~~~~~~~~~~~~~~~~

Before starting with the new version, you should do pre-flight checks
to ensure everything is fine. If any of those check fail, the upgrade
should stop to let the deployer chose what to do.

Making sure LBaaS v1 isn't in the way
`````````````````````````````````````

Because LBaaS was deprecated, this playbook checks if it was previously
deployed, and fails if this is the case.

See :ref:`lbaas-version-check` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/lbaas-version-check.yml"

Cleanup old facts
~~~~~~~~~~~~~~~~~

Some configuration changed, and old facts should be purged before
the upgrade.

See :ref:`fact-cleanup-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/ansible_fact_cleanup.yml"

Update configuration and environment files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user configuration files in ``/etc/openstack_deploy/`` and the environment
layout in ``/etc/openstack_deploy/env.d`` have new name
values added in Newton.

See :ref:`config-change-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml"

Update user secrets file
~~~~~~~~~~~~~~~~~~~~~~~~

Newton introduces new user secrets to the stack. These are populated
automatically with the following playbook.

See :ref:`user-secrets-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/user-secrets-adjustment.yml"

Update database collations
~~~~~~~~~~~~~~~~~~~~~~~~~~

The default database collation has been changed to `utf8_general_ci`. This play
performs a conversion on existing databases and tables.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/db-collation-alter.yml

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
after other Galera containers have been restarted in the previous step.

Cleanup ``pip.conf`` file in the ``repo_servers``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a ``pip.conf`` file exists within the repository server
infrastructure, it can cause build failures when upgrading
to Newton. This play removes the ``pip.conf`` file from the repository
servers.

See :ref:`repo-server-pip-conf-removal` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/repo-server-pip-conf-removal.yml"

Ensure hostname aliases are created for non-RFC1034/35 hostnames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure an alias is created for non-RFC1034/35 hostnames.

See :ref:`old-hostname-compatibility` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/old-hostname-compatibility.yml"

Upgrade infrastructure
~~~~~~~~~~~~~~~~~~~~~~

Running the standard OpenStack-Ansible infrastructure playbook applies the
relevant Newton settings and packages. This upgrade is required for the Newton
release of OpenStack-Ansible.

For certain versions of Mitaka, you must upgrade the RabbitMQ service.

See :ref:`setup-infra-playbook` for details.

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'galera_upgrade=true' \
    -e 'rabbitmq_upgrade=true'

Flush Memcached cache
~~~~~~~~~~~~~~~~~~~~~

See :ref:`memcached-flush` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/memcached-flush.yml"

Upgrade OpenStack
~~~~~~~~~~~~~~~~~

Upgrade the OpenStack components with the same installation playbook,
without any additional options.

.. code-block:: console

    # openstack-ansible setup-openstack.yml

--------------

.. include:: navigation.txt
