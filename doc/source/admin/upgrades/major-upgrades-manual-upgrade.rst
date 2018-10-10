.. _upgrading-manually:

Upgrading manually
==================

Deployers can run the upgrade steps manually. Manual upgrades are useful for
scoping the changes in the upgrade process (for example, in very large
deployments with strict SLA requirements), or performing other upgrade
automations beyond what is provided by OpenStack-Ansible.

The steps detailed here match those performed by the ``run-upgrade.sh``
script. You can safely run these steps multiple times.

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

From the ``openstack-ansible`` root directory, run the following commands:

.. code-block:: console

    # export MAIN_PATH="$(pwd)"
    # export SCRIPTS_PATH="${MAIN_PATH}/scripts"
    # export UPGRADE_PLAYBOOKS="${SCRIPTS_PATH}/upgrade-utilities/playbooks"

Deal with existing OpenStack-Ansible artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The deployment node may have previous branch artifacts.

Unset the following environment variables first:

.. code-block:: console

    # unset ANSIBLE_INVENTORY

Optionally, take a backup of your environment:

.. code-block:: console

    # tar zcf /openstack/previous-ansible_`date +%F_%H%M`.tar.gz /etc/openstack_deploy /etc/ansible/ /usr/local/bin/openstack-ansible.rc

Bootstrap Ansible again
~~~~~~~~~~~~~~~~~~~~~~~

Bootstrap Ansible again to ensure that all OpenStack-Ansible role
dependencies are in place before you run playbooks from the
|current_release_formal_name| release.

.. code-block:: console

    # ${SCRIPTS_PATH}/bootstrap-ansible.sh

Change to the playbooks directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change to the playbooks directory so that the OpenStack-Ansible dynamic
inventory is found automatically.

.. code-block:: console

    # cd playbooks

Preflight checks
~~~~~~~~~~~~~~~~

Before starting with the upgraded version, perform preflight checks to ensure
your environment is stable. If any of those checks fail, the upgrade should
stop to let the deployer chose what to do.

Clean up old facts
~~~~~~~~~~~~~~~~~~

Some configurations have changed, so purge old facts before
the upgrade. For more information, see :ref:`fact-cleanup-playbook`.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/ansible_fact_cleanup.yml"

Update configuration and environment files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user configuration files in the ``/etc/openstack_deploy/`` directory and
the environment layout in the ``/etc/openstack_deploy/env.d`` directory have
new name values added in |current_release_formal_name|. Update the files as
follows. For more information, see :ref:`config-change-playbook`.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml"

Update user secrets file
~~~~~~~~~~~~~~~~~~~~~~~~

|current_release_formal_name| introduces new user secrets to the stack.
These secrets are populated automatically when you run the following playbook.
For more information, see :ref:`user-secrets-playbook`.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/user-secrets-adjustment.yml"

Clean up the pip.conf file
~~~~~~~~~~~~~~~~~~~~~~~~~~

The presence of the ``pip.conf`` file can cause build failures during the
upgrade to |current_release_formal_name|. This playbook removes the
``pip.conf`` file on all the physical servers and on the repo containers.
For more information, see :ref:`pip-conf-removal`.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/pip-conf-removal.yml"

Clean up the ceph-ansible galaxy namespaced roles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ceph-ansible common roles are no longer namespaced with a galaxy-style
'.' (ie. ``ceph.ceph-common`` is now cloned as ``ceph-common``), due to a
change in the way upstream meta dependencies are handled in the ceph roles.
The roles will be cloned according to the new naming, and an upgrade
playbook ``ceph-galaxy-removal.yml`` has been added to clean up the stale
galaxy-named roles.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/ceph-galaxy-removal.yml"

Clean up the molteniron role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The molteniron service is not an official OpenStack project, and has been
removed from the integrated build. It can still be optionally added, but
due to the fact that it was previously integrated we need to remove it
during this major upgrade to ensure that the repo build process does not
try to build its wheels.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/molteniron-role-removal.yml"

Upgrade hosts
~~~~~~~~~~~~~

Before installing the infrastructure and OpenStack, update the host machines.

.. code-block:: console

    # openstack-ansible setup-hosts.yml --limit '!galera_all:!neutron_agent:!rabbitmq_all'

This command is the same setting up hosts on a new installation. The
``galera_all`` host group is excluded to prevent reconfiguration and
restarting of any Galera containers.

Update Galera LXC container configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the Galera container configuration independently.

.. code-block:: console

    # openstack-ansible lxc-containers-create.yml -e \
    'lxc_container_allow_restarts=false' --limit 'galera_all:neutron_agent:rabbitmq_all'

This command is a subset of the host setup playbook, limited to the
``galera_all`` host group. The configuration of those containers is
updated but a restart for any changes to take effect is deferred to another
playbook (see the next section).

Perform a controlled rolling restart of the Galera containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Restart containers one at a time, ensuring that each is started, responding,
and synchronized with the other nodes in the cluster before moving on to the
next. This step allows the LXC container configuration that you applied earlier
to take effect, ensuring that the containers are restarted in a controlled
fashion.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/galera-cluster-rolling-restart.yml"

Update repository servers
~~~~~~~~~~~~~~~~~~~~~~~~~

Update the configuration of the repository servers and build new packages
required by the |current_release_formal_name| release.

.. code-block:: console

    # openstack-ansible repo-install.yml

Update HAProxy configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install and update any new or changed HAProxy service configurations.

.. code-block:: console

    # openstack-ansible haproxy-install.yml

Use the repository servers
~~~~~~~~~~~~~~~~~~~~~~~~~~

Now all containers can be pointed to the repo server's VIPs.

.. code-block:: console

    # openstack-ansible repo-use.yml

Upgrade the MariaDB version
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upgrade MariaDB to the most recent 10.x minor release across the cluster.

.. code-block:: console

    # openstack-ansible galera-install.yml -e 'galera_upgrade=true'

Upgrade the infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following commands perform all of the steps from the setup-infrastructure
playbook, except for ``repo-install.yml``, ``haproxyinstall.yml``, and
``galera-install.yml`` which you ran earlier.
Running these playbook applies the relevant |current_release_formal_name|
settings and packages.

For certain versions of |previous_release_formal_name|, you must upgrade
the RabbitMQ service.

For more information, see :ref:`setup-infra-playbook`.

.. code-block:: console

    # openstack-ansible unbound-install.yml
    # openstack-ansible memcached-install.yml
    # openstack-ansible rabbitmq-install.yml -e 'rabbitmq_upgrade=true'
    # openstack-ansible etcd-install.yml
    # openstack-ansible utility-install.yml
    # openstack-ansible rsyslog-install.yml

Flush Memcached cache
~~~~~~~~~~~~~~~~~~~~~

Flush all of the caches in Memcached. For more information,
see :ref:`memcached-flush`.

.. code-block:: console

    # openstack-ansible "${UPGRADE_PLAYBOOKS}/memcached-flush.yml"

Upgrade OpenStack
~~~~~~~~~~~~~~~~~

Upgrade the OpenStack components with the same installation
playbook, without any additional options.

.. code-block:: console

    # openstack-ansible setup-openstack.yml
