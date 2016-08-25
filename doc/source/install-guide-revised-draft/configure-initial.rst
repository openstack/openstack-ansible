=================================
Initial environment configuration
=================================

OpenStack-Ansible depends on various files that are used to build an inventory
for Ansible. Start by getting those files into the correct places:

#. Copy the contents of the
   ``/opt/openstack-ansible/etc/openstack_deploy`` directory to the
   ``/etc/openstack_deploy`` directory.

.. note::

    As of Newton, the ``env.d`` directory has been moved from this source
    directory to ``playbooks/inventory/``.

#. Change to the ``/etc/openstack_deploy`` directory.

#. Copy the ``openstack_user_config.yml.example`` file to
   ``/etc/openstack_deploy/openstack_user_config.yml``.

You can review the ``openstack_user_config.yml`` file and make changes
to the deployment of your OpenStack environment.

.. note::

   The file is heavily commented with details about the various options.

Configuration in ``openstack_user_config.yml`` defines which hosts
will run the containers and services deployed by OpenStack-Ansible. For
example, hosts listed in the ``shared-infra_hosts`` run containers for many of
the shared services that your OpenStack environment requires. Some of these
services include databases, memcached, and RabbitMQ. There are several other
host types that contain other types of containers and all of these are listed
in ``openstack_user_config.yml``.

For details about how the inventory is generated from the environment
configuration, see :ref:`developer-inventory`.

--------------

.. include:: navigation.txt
