Upgrade Playbooks
=================

This section describes the playbooks that are used in the upgrade process in
further detail.

Within the main :file:`scripts` directory there is an :file:`upgrade-utilities`
directory, which contains an additional playbooks directory. These playbooks
facilitate the upgrade process.

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

Additionally, the following changes will be made to the environment and
configuration of container memberships.

    * ``aodh.yml`` and ``haproxy.yml`` will be copied from the source tree into
        ``/etc/openstack_deploy/env.d``.
    * ``/etc/openstack_deploy/env.d/neutron.yml`` will have LBaaS group
      memberships added. See :ref:`neutron-env-script` for details.
    * ``/etc/openstack_deploy/env.d/ceilometer.yml`` will have two alarm group
      memberships changed. See :ref:`ceilo-env-script` for details.

--------------

.. include:: navigation.txt
