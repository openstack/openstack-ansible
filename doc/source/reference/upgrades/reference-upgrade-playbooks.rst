Major Upgrade Playbooks
=======================

This section provides details about the playbooks that are used in the
upgrade process. Within the main :file:`scripts` directory there is an
:file:`upgrade-utilities` directory, which contains an additional playbooks
directory. These playbooks facilitate the upgrade process.

.. _fact-cleanup-playbook:

ansible_fact_cleanup.yml
~~~~~~~~~~~~~~~~~~~~~~~~

This playbook calls a script to remove files in the
``/etc/openstack_deploy/ansible_facts/`` directory.

.. _config-change-playbook:

deploy-config-changes.yml
~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook backs up the ``/etc/openstack_deploy`` directory before
changing the configuration.

The``/etc/openstack_deploy`` directory is copied once to the
|upgrade_backup_dir| directory.

.. _user-secrets-playbook:

user-secrets-adjustment.yml
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook ensures that the user secrets file is updated based on the
example file in the main repository, making it possible to guarantee that all
secrets move into the upgraded environment and are generated appropriately.
This playbook adds only new secrets, such as those necessary for new services
or new settings added to existing services. Values that were set previously are
not changed.

.. _pip-conf-removal:

pip-conf-removal.yml
~~~~~~~~~~~~~~~~~~~~

The presence of the ``pip.conf`` file locks down all Python installations to
packages on the repo servers. If this file exists on a repo server or a
physical node, it causes a circular dependency issue and the upgrade fails.
This playbook removes the file on all the repo servers and physical nodes.

.. _ceph-galaxy-removal:

ceph-galaxy-removal.yml
~~~~~~~~~~~~~~~~~~~~~~~

The ceph-ansible common roles are no longer namespaced with a galaxy-style
'.' (ie. ``ceph.ceph-common`` is now cloned as ``ceph-common``), due to a
change in the way upstream meta dependencies are handled in the ceph roles.
The roles will be cloned according to the new naming, and an upgrade
playbook ``ceph-galaxy-removal.yml`` has been added to clean up the stale
galaxy-named roles.

.. _molteniron-role-removal:

Clean up the molteniron role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The molteniron service is not an official OpenStack project, and has been
removed from the integrated build. It can still be optionally added, but
due to the fact that it was previously integrated we need to remove it
during this major upgrade to ensure that the repo build process does not
try to build its wheels. The upgrade playbook ``molteniron-role-removal.yml``
has been added to clean it up.

.. _setup-infra-playbook:

setup-infrastructure.yml
~~~~~~~~~~~~~~~~~~~~~~~~

The ``playbooks`` directory contains the ``setup-infrastructure.yml`` playbook.
The ``run-upgrade.sh`` script calls the ``setup-insfrastructure.yml`` playbook
with specific arguments to upgrade MariaDB and RabbitMQ.

For example, to run an upgrade for both components at once, run the following
commands:

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'rabbitmq_upgrade=true' \
      -e 'galera_upgrade=true'

The ``rabbitmq_upgrade`` variable tells the ``rabbitmq_server`` role to
upgrade RabbitMQ.

.. note::
    The RabbitMQ server role installs patch releases automatically,
    regardless of the value of ``rabbitmq_upgrade``. This variable
    controls the upgrade of only the major or minor versions.

    Upgrading RabbitMQ in the |current_release_formal_name| release is optional. The
    ``run-upgrade.sh`` script does not automatically upgrade it. To upgrade
    RabbitMQ, insert the ``rabbitmq_upgrade: true``
    line into a file, such as ``/etc/openstack_deploy/user_variables.yml``.

The ``galera_upgrade`` variable tells the ``galera_server`` role to remove the
current version of MariaDB and Galera and upgrade to the 10.*x* series.

.. _memcached-flush:

memcached-flush.yml
~~~~~~~~~~~~~~~~~~~

This playbook sends the ``flush_all`` command to Memcached with the help of
netcat.
