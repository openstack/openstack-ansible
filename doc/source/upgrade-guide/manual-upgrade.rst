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

Check out the |current_release_formal_name| release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure your OpenStack-Ansible code is on the latest
|current_release_formal_name| tagged release.

.. parsed-literal::

    # git checkout |latest_tag|

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

Re-bootstrap Ansible for |current_release_formal_name|
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bootstrapping Ansible again ensures that all OpenStack-Ansible role
dependencies are in place before running playbooks from the
|current_release_formal_name| release.

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
values added in |current_release_formal_name|.

See :ref:`config-change-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml"

Update user secrets file
~~~~~~~~~~~~~~~~~~~~~~~~

|current_release_formal_name| introduces new user secrets to the stack.
These are populated automatically with the following playbook.

See :ref:`user-secrets-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/user-secrets-adjustment.yml"

Cleanup old MariaDB apt repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default MariaDB apt repositories have been changed to use HTTP instead of
HTTPS. This playbook removes existing repositories of the previous default.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/mariadb-apt-cleanup.yml"

Update database collations
~~~~~~~~~~~~~~~~~~~~~~~~~~

The default database collation has been changed to `utf8_general_ci`. This play
performs a conversion on existing databases and tables.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/db-collation-alter.yml"

Cleanup pip.conf file
~~~~~~~~~~~~~~~~~~~~~

The presence of ``pip.conf`` file can cause build failures when upgrading to
|current_release_formal_name|. This play removes the ``pip.conf`` file
on all the physical servers and on the repo containers.

See :ref:`pip-conf-removal` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/pip-conf-removal.yml"

Upgrade hosts
~~~~~~~~~~~~~

Before installing the infrastructure and OpenStack, update the host machines.

.. code-block:: console

    # openstack-ansible setup-hosts.yml --limit '!galera_all'

This command is the same as doing host setups on a new install. The
``galera_all`` host group is excluded to prevent reconfiguration and
restarting of any Galera containers.

Update Galera LXC container configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the Galera container configuration independently.

.. code-block:: console

    # openstack-ansible lxc-containers-create.yml -e \
    'lxc_container_allow_restarts=false' --limit galera_all

This command is a subset of the host setup playbook, limited to the
``galera_all`` host group. The configuration of those containers will be
updated but a restart for any changes to take effect will be deferred to a
later playbook.

Perform a controlled rolling restart of the galera containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Restart containers one at a time, ensuring that each is up, responding,
and synced with the other nodes in the cluster, before moving on to the
next. This step allows the lxc container config applied earlier to take
effect, ensuring that the containers are restarted in a controlled fashion.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/galera-cluster-rolling-restart.yml"

Update HAProxy configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install and update any new or changed HAProxy service configurations.

.. code-block:: console

    # openstack-ansible haproxy-install.yml

Update repo servers
~~~~~~~~~~~~~~~~~~~

Update the configuration of the repo servers and build new packages required by
the |current_release_formal_name| release.

.. code-block:: console

    # openstack-ansible repo-install.yml

Ensure hostname aliases are created for non-RFC1034/35 hostnames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure an alias is created for non-RFC1034/35 hostnames.

See :ref:`old-hostname-compatibility` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/old-hostname-compatibility.yml"

Perform a mariadb version upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update mariadb to the most 10.0 minor release across the cluster.

.. code-block:: console

    # openstack-ansible galera-install.yml -e 'galera_upgrade=true'

Upgrade infrastructure
~~~~~~~~~~~~~~~~~~~~~~

The following commands perform all steps from the setup-infrastructure
playbook, except for `repo-install.yml``, ``haproxyinstall.yml``, and
`galera-install.yml`` which we ran earlier.
Running these playbook applies the relevant |current_release_formal_name|
settings and packages.

For certain versions of |previous_release_formal_name|, you must upgrade
the RabbitMQ service.

See :ref:`setup-infra-playbook` for details.

.. code-block:: console

    # openstack-ansible memcached-install.yml
    # openstack-ansible rabbitmq-install.yml -e 'rabbitmq_upgrade=true'
    # openstack-ansible utility-install.yml
    # openstack-ansible rsyslog-install.yml

Flush Memcached cache
~~~~~~~~~~~~~~~~~~~~~

See :ref:`memcached-flush` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/memcached-flush.yml"

Stop and remove ``aodh-api`` service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`aodh-api-init-delete` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/aodh-api-init-delete.yml"

Stop and remove ``ceilometer-api`` service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`ceilometer-api-init-delete` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/ceilometer-api-init-delete.yml"

Upgrade OpenStack
~~~~~~~~~~~~~~~~~

Upgrade the OpenStack components with the same installation
playbook, without any additional options.

.. code-block:: console

    # openstack-ansible setup-openstack.yml
