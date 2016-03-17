Upgrade Playbooks
=================

This section describes the playbooks that are used in the upgrade process in
further detail.

Within the main :file:`scripts` directory there is an :file:`upgrade-utilities`
directory, which contains an additional playbooks directory. These playbooks
facilitate the upgrade process.

.. _cleanup-rabbit-playbook:

cleanup-rabbitmq-vhost.yml
--------------------------
Liberty has introduced separate vhosts and RabbitMQ users for the OpenStack
services. This playbook is designed to clean up the remnants of the previous
RabbitMQ configuration, this means removing the shared RabbitMQ user
'openstack' and the exchanges and queues in the / vhost that aren't there by
default. This playbook should not be run until after all the services have
stopped using the shared configuration.

.. _config-change-playbook:

deploy-config-changes.yml
-------------------------

This playbook will back up the ``/etc/openstack_deploy`` directory before
making the necessary changes to the configuration.

``/etc/openstack_deploy`` is copied once to ``/etc/openstack_deploy.KILO``.
The copy happens only once, so repeated runs are safe.

Additionally, the following changes will be made to the environment,
configuration of container memberships, and user variables.

    * ``aodh.yml`` and ``haproxy.yml`` will be copied from the source tree into
        ``/etc/openstack_deploy/env.d``.
    * ``/etc/openstack_deploy/env.d/neutron.yml`` will have LBaaS group
      memberships added. See :ref:`neutron-env-script` for details.
    * ``/etc/openstack_deploy/env.d/ceilometer.yml`` will have two alarm group
      memberships changed. See :ref:`ceilo-env-script` for details.
    * ``/etc/openstack_deploy/user_*.yml`` will have old variable names
      updated to reflect new ones. See :ref:`migrate-os-vars` for details.

.. _user-secrets-playbook:

user-secrets-adjustments.yml
----------------------------

This playbook ensures that the user secrets file is updated based on the example
file in the main repository. This makes it possible to guarantee all secrets are
carried into the upgraded environment and appropriately generated. Only new
secrets are added, such as those necessary for new services or new settings
added to existing services. Previously set values will not be changed.

.. _setup-infra-playbook:

setup-infrastructure.yml
------------------------

The ``setup-infrastructure.yml`` playbook is contained in the main
``playbooks`` directory, but is called by ``run-upgrade.sh`` with specific
arguments in order to upgrade infrastructure components such as MariaDB and
RabbitMQ.

For example, to run an upgrade for both components at once, run the following:

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'rabbitmq_upgrade=true' \
    # -e 'galera_upgrade=true'

The ``rabbitmq_upgrade`` variable tells the ``rabbitmq_server`` role to
upgrade the running major/minor version of RabbitMQ.

.. note::
    The RabbitMQ server role will install patch releases automatically,
    regardless of the value of ``rabbitmq_upgrade``. This variable only
    controls upgrading the major or minor version.

    Upgrading RabbitMQ in the Liberty release is optional. The
    ``run-upgrade.sh`` script will not automatically upgrade it. If a RabbitMQ
    upgrade using the script is desired, insert the ``rabbitmq_upgrade: true``
    line into a file such as ``/etc/openstack_deploy/user_variables.yml``.

The ``galera_upgrade`` variable tells the ``galera_server`` role to remove the
current version of MariaDB/Galera and upgrade to the 10.x series. This upgrade
is required for Liberty.

.. _neutron-port-sec-playbook:

disable-neutron-port-security.yml
---------------------------------

In Kilo, Neutron introduced a port security extension to ML2, but did not
enable it. OpenStack-Ansible enabled this extension by default in Liberty.
However, networks created prior to enabling the port security extension do not
receive any port security information. When VMs are started or created while
attached to these networks, the start up or creation will fail.

Neutron itself does not currently provide a mechanism for cleanly applying the
port security bindings to pre-existing networks.

In order to avoid this behavior, OpenStack-Ansible will disable port security
bindings for environments upgraded from Kilo to Liberty.

The following stanza will be added to
``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    neutron_ml2_conf_ini_overrides:
      ml2:
        extension_drivers: ''

--------------

.. include:: navigation.txt
