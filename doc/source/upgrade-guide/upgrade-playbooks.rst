Upgrade Playbooks
=================

This section describes the playbooks that are used in the upgrade process in
further detail.

Within the main :file:`scripts` directory there is an :file:`upgrade-utilities`
directory, which contains an additional playbooks directory. These playbooks
facilitate the upgrade process.

.. _cleanup-rabbit-playbook:

``cleanup-rabbitmq-vhost.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Liberty introduces separate vhost and RabbitMQ users for the OpenStack
services. This playbook cleans up the remnants of the previous
RabbitMQ configuration, removes the shared RabbitMQ user
`openstack`, and clears the exchanges and queues in the vhost that
are not there by default.

.. note::

   Do not run this playbook until after all the services have
   stopped using the shared configuration.

.. _fact-cleanup-playbook:

``ansible_fact_cleanup.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This calls a script to removes files in ``/etc/openstack_deploy/ansible_facts/``

.. _config-change-playbook:

``deploy-config-changes.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook backs up the ``/etc/openstack_deploy`` directory before
making the necessary changes to the configuration.

``/etc/openstack_deploy`` copies once to ``/etc/openstack_deploy.KILO``.

As a result, the following changes are made to the environment,
configuration of container memberships, and user variables:

    * Copy ``aodh.yml`` and ``haproxy.yml`` from the source tree into
        ``/etc/openstack_deploy/env.d``.
    * ``/etc/openstack_deploy/env.d/neutron.yml`` adds LBaaS group
      memberships. See :ref:`neutron-env-script` for details.
    * ``/etc/openstack_deploy/env.d/ceilometer.yml`` changes two alarm group
      memberships. See :ref:`ceilo-env-script` for details.
    * ``/etc/openstack_deploy/user_*.yml`` updates old variable names
      to reflect new ones. See :ref:`migrate-os-vars` for details.

.. _user-secrets-playbook:

``user-secrets-adjustment.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updates to this playbook ensure that the user secrets file is based on the example
file in the main repository. This makes it possible to guarantee all
secrets move into the upgraded environment and generate appropriately.
This adds only new secrets, such as those necessary for new services or new settings
added to existing services. Values set previously are not changed.

.. _setup-infra-playbook:

``repo-server-pip-conf-removal.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook ensures the repository servers do not have the ``pip.conf`` in the
root ``pip`` directory. This locks down the Python packages available to install.
If this file exists on the repository servers, it causes build failures.

.. _repo-server-pip-conf-removal:

``setup-infrastructure.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main ``playbooks`` directory contains the ``setup-infrastructure.yml`` playbook.
However, ``run-upgrade.sh`` calls it with specific arguments to upgrade
infrastructure components such as MariaDB and RabbitMQ.

For example, to run an upgrade for both components at once, run the following command:

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'rabbitmq_upgrade=true' \
    # -e 'galera_upgrade=true'

The ``rabbitmq_upgrade`` variable tells the ``rabbitmq_server`` role to
upgrade the running major or minor versions of RabbitMQ.

.. note::

    The RabbitMQ server role installs patch releases automatically,
    regardless of the value of ``rabbitmq_upgrade``. This variable only
    controls upgrading the major or minor versions.

    Upgrading RabbitMQ in the Liberty release is optional. The
    ``run-upgrade.sh`` script does not automatically upgrade it. To upgrade RabbitMQ,
    insert the ``rabbitmq_upgrade: true``
    line into a file, such as: ``/etc/openstack_deploy/user_variables.yml``.

The ``galera_upgrade`` variable tells the ``galera_server`` role to remove the
current version of MariaDB and Galera and upgrade to the 10.x series. Liberty requires
this upgrade.

.. _neutron-port-sec-playbook:

``disable-neutron-port-security.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Kilo, neutron introduces a port security extension to ML2, but does not
enable it. OpenStack-Ansible enables this extension by default in Liberty.
However, networks created prior to enabling the port security extension do not
receive any port security information. Start up creation fails when starting
or creating VMs while attached to these networks.

Neutron does not currently provide a mechanism for applying the
port security bindings cleanly to pre-existing networks.

In order to avoid this behavior, OpenStack-Ansible disables port security
bindings for environments upgraded from Kilo to Liberty.

The following stanza adds to
``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    neutron_ml2_conf_ini_overrides:
      ml2:
        extension_drivers: ''

``mariadb-apt-cleanup.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook cleans up older MariaDB apt repositories which used HTTP instead
of HTTPS.

.. _memcached-flush:

``memcached-flush.yml``
~~~~~~~~~~~~~~~~~~~~~~~

Sends "flush_all" to memcached with the help of nc.

.. _glance-db-storage-url-fix:

``glance-db-storage-url-fix.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The upgrade playbook ``glance-db-storage-url-fix.yml`` will
migrate all existing Swift backed Glance images inside the
image_locations database table from a Keystone v2 API URL to a v3 URL.
This will force the Swift client to operate against a v3 Keystone URL.
A backup of the old image_locations table is stored inside a new database
table ``image_locations_keystone_v3_mig_pre_liberty`` and can be safely
removed after a successfull upgrade to Liberty.
This upgrade task is related to
``https://bugs.launchpad.net/openstack-ansible/+bug/1582279``

--------------

.. include:: navigation.txt
