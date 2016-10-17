.. _manual-upgrade:

Manual Upgrade Steps
====================

The steps detailed here match those performed by the ``run-upgrade.sh``
script. Any of these steps can safely be run multiple times.

Check out the Mitaka release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure your OpenStack-Ansible code is on the latest Mitaka release tag (13.x.x).

.. code-block:: console

    # git checkout stable/mitaka
    # LATEST_TAG=$(git describe --abbrev=0 --tags)
    # git checkout ${LATEST_TAG}

Preparing the shell variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Re-bootstrap Ansible for Mitaka
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bootstrapping Ansible again ensures that all OpenStack-Ansible role
dependencies are in place before running playbooks from the Mitaka
release.

.. code-block:: console

    # ${SCRIPTS_PATH}/bootstrap-ansible.sh

Change to playbooks directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change to the playbooks directory so that the OpenStack-Ansible dynamic
inventory is found automatically.

.. code-block:: console

    # cd playbooks

Clean up old facts
~~~~~~~~~~~~~~~~~~

Purge old facts before beginning the upgrade.

See :ref:`fact-cleanup-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/01_ansible_fact_cleanup.yml"

Update configuration and environment files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user configuration files in ``/etc/openstack_deploy/`` and the environment
layout in ``/etc/openstack_deploy/env.d`` have new name
values added in Mitaka.

See :ref:`config-change-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml"

Update user secrets file
~~~~~~~~~~~~~~~~~~~~~~~~

Mitaka introduces new user secrets to the stack. These are populated
automatically with the following playbook.

See :ref:`user-secrets-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/user-secrets-adjustment.yml"

Cleanup ``pip.conf`` file
~~~~~~~~~~~~~~~~~~~~~~~~~

The presence of ``pip.conf`` file can cause build failures when upgrading to
Mitaka. This play removes the ``pip.conf`` file on all the physical servers
and on the repo containers.

See :ref:`pip-conf-removal` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/pip-conf-removal.yml"

Ensure hostname aliases are created for non-RFC1034/35 hostnames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure an alias is created for non-RFC1034/35 hostnames.

See :ref:`old-hostname-compatibility` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/old-hostname-compatibility.yml"

Upgrade hosts
~~~~~~~~~~~~~

The next step is upgrading your hosts. Avoid upgrading the Galera cluster
nodes to prevent changes in the cluster.

.. code-block:: console

   # openstack-ansible setup-hosts.yml --limit '!galera_all'

Restart Rabbitmq containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This ensures the rabbitmq nodes are using their proper new hostnames.

See :ref:`restart-rabbitmq` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/restart-rabbitmq-containers.yml"

Clean up old facts
~~~~~~~~~~~~~~~~~~

Facts are purged as container hostnames have changed after running the
``old-hostname-compatibility.yml`` playbook. Failing to do this could
result in a failure in upgrading RabbitMQ.

See :ref:`fact-cleanup-playbook` for more details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/02_ansible_fact_cleanup.yml"

Update Galera LXC container configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``setup-hosts.yml`` playbook above skipped the Galera nodes. In this step,
the ``lxc-container-create.yml`` playbook applies changes to Galera containers
while preventing them from restarting.

.. code-block:: console

   # openstack-ansible lxc-containers-create.yml -e \
     'lxc_container_allow_restarts=false' --limit galera_all

Upgrade repositories
~~~~~~~~~~~~~~~~~~~~

Running the OpenStack-Ansible ``repo-install.yml`` playbook
prepares the repo server with all the packages needed for Mitaka.

.. code-block:: console

   # openstack-ansible repo-install.yml

Upgrade Galera
~~~~~~~~~~~~~~

Running the OpenStack-Ansible ``galera-install.yml`` playbook
ensures Galera is running on the latest Mitaka.

.. code-block:: console

   # openstack-ansible galera-install.yml -e 'galera_upgrade=true'

Restart Galera
~~~~~~~~~~~~~~

After the Galera update in the previous step, restart the cluster
in a controlled fashion.

.. code-block:: console

   # openstack-ansible "${UPGRADE_PLAYBOOKS}/galera-cluster-rolling-restart.yml"

Upgrade the remaining infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the remaining parts of the ``setup-infrastructure.yml`` playbook.

.. code-block:: console

   # openstack-ansible haproxy-install.yml
   # openstack-ansible memcached-install.yml
   # openstack-ansible rabbitmq-install.yml -e 'rabbitmq_upgrade=true'
   # openstack-ansible utility-install.yml
   # openstack-ansible rsyslog-install.yml

Flush Memcached cache
~~~~~~~~~~~~~~~~~~~~~

See :ref:`memcached-flush` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/memcached-flush.yml"

Populate neutron MTUs
~~~~~~~~~~~~~~~~~~~~~

See :ref:`neutron-mtu-migration` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/neutron-mtu-migration.yml"


Upgrade OpenStack
~~~~~~~~~~~~~~~~~

Upgrade the OpenStack components with the same installation playbook,
without any additional options.

.. code-block:: console

    # openstack-ansible setup-openstack.yml

Clean up Databases for RFC 1034 and 1035
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``rfc1034_1035-cleanup.yml`` playbook to remove invalid
hostnames that may still be within the databases.

See :ref:`rfc1034-1035-cleanup` for details.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/rfc1034_1035-cleanup.yml"

--------------

.. include:: navigation.txt
