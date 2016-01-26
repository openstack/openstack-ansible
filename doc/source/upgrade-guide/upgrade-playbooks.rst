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

--------------

.. include:: navigation.txt
