Upgrade Playbooks
=================

This section describes the playbooks that are used in the upgrade process in
further detail.

Within the main :file:`scripts` directory there is an :file:`upgrade-utilities`
directory, which contains an additional playbooks directory. These playbooks
facilitate the upgrade process.

.. _fact-cleanup-playbook:

``ansible_fact_cleanup.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This calls a script to removes files in ``/etc/openstack_deploy/ansible_facts/``

.. _config-change-playbook:

``deploy-config-changes.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook backs up the ``/etc/openstack_deploy`` directory before
changing the configuration.

``/etc/openstack_deploy`` copies once to ``/etc/openstack_deploy.LIBERTY``.

.. _user-secrets-playbook:

``user-secrets-adjustment.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook ensures that the user secrets file is updated based on the example
file in the main repository, making it possible to guarantee all secrets move
into the upgraded environment and generate appropriately.
This adds only new secrets, such as those necessary for new services or new settings
added to existing services. Values set previously are not changed.

.. _pip-conf-removal:

``pip-conf-removal.yml``
~~~~~~~~~~~~~~~~~~~~~~~~

The presence of ``pip.conf`` locks down all Python installations to packages on the
repo servers. If ``pip.conf`` exists on a repo server or a physical node, it will
cause a circular dependency issue and the upgrade will fail.

.. _old-hostname-compatibility:

``old-hostname-compatibility.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook ensures an alias is created for old hostnames that may not be RFC
1034 or 1035 compatible. Using a hostname alias allows agents to continue working
in cases where the hostname is also the registered agent name. This playbook is
only needed for upgrades of in-place upgrades of existing nodes or if a node is replaced or
rebuilt it will be brought into the cluster using a compliant hostname.

.. _restart-rabbitmq:

``restart-rabbitmq-containers``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook restarts the rabbitmq nodes serially (1 at a time), and waits
for rabbitmq to be back up before continuing.

.. _setup-infra-playbook:

``setup-infrastructure.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``playbooks`` directory contains the ``setup-infrastructure.yml`` playbook.
The ``run-upgrade.sh`` script calls ``setup-insfrastructure.yml`` with specific
arguments to upgrade MariaDB and RabbitMQ.

For example, to run an upgrade for both components at once, run the following commands:

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'rabbitmq_upgrade=true' \
    # -e 'galera_upgrade=true'

The ``rabbitmq_upgrade`` variable tells the ``rabbitmq_server`` role to
upgrade RabbitMQ.

.. note::
    The RabbitMQ server role installs patch releases automatically,
    regardless of the value of ``rabbitmq_upgrade``. This variable only
    controls upgrading the major or minor versions.

    Upgrading RabbitMQ in the Mitaka release is optional. The
    ``run-upgrade.sh`` script does not automatically upgrade it. To upgrade RabbitMQ,
    insert the ``rabbitmq_upgrade: true``
    line into a file, such as: ``/etc/openstack_deploy/user_variables.yml``.

The ``galera_upgrade`` variable tells the ``galera_server`` role to remove the
current version of MariaDB and Galera and upgrade to the 10.x series.

.. _memcached-flush:

``memcached-flush.yml``
~~~~~~~~~~~~~~~~~~~~~~~

Sends ``flush_all`` to memcached with the help of nc.

.. _neutron-mtu-migration:

``neutron-mtu-migration.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the MTU setting for networks within neutron. When migrating from Liberty to Mitaka
neutron does not automatically set or migrate networks. Neutron has no migration to
correctly set the MTU on existing networks created in Liberty or below. This work-around
sets the MTU on these networks before the upgrade starts so that instances booted on these
networks after the upgrade has finished will have their MTUs set correctly.

.. _rfc1034-1035-cleanup:

``rfc1034_1035-cleanup.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook ensures the OpenStack service databases for heat, nova, neutron,
and cinder are cleaned up with regard to actively registered services. These
OpenStack services register nodes within the environment using the hostname as
a unique key and in previous releases containers had invalid hostnames. This
playbook will remove invalid service/agent entries that are found within the
database and meet the invalid hostname criteria.

--------------

.. include:: navigation.txt
