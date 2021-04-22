.. _configuring-inventory:

Configuring the inventory
=========================

In this chapter, you can find the information on how to configure
the openstack-ansible dynamic inventory to your needs.

Introduction
~~~~~~~~~~~~

Common OpenStack services and their configuration are defined by
OpenStack-Ansible in the
``/etc/openstack_deploy/openstack_user_config.yml`` settings file.

Additional services should be defined with a YAML file in
``/etc/openstack_deploy/conf.d``, in order to manage file size.

The ``/etc/openstack_deploy/env.d`` directory sources all YAML files into the
deployed environment, allowing a deployer to define additional group mappings.
This directory is used to extend the environment skeleton, or modify the
defaults defined in the ``inventory/env.d`` directory.

To understand how the dynamic inventory works, see
:ref:`inventory-in-depth`.

.. warning::

   Never edit or delete the files
   ``/etc/openstack_deploy/openstack_inventory.json`` or
   ``/etc/openstack_deploy/openstack_hostnames_ips.yml``. This can
   lead to file corruptions, and problems with the inventory: hosts
   and container could disappear and new ones would appear,
   breaking your existing deployment.


Configuration constraints
~~~~~~~~~~~~~~~~~~~~~~~~~

Group memberships
-----------------

When adding groups, keep the following in mind:

* A group can contain hosts
* A group can contain child groups

However, groups cannot contain child groups and hosts.

The lxc_hosts Group
-------------------

When the dynamic inventory script creates a container name, the host on
which the container resides is added to the ``lxc_hosts`` inventory group.

Using this name for a group in the configuration will result in a runtime
error.

Deploying directly on hosts
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To deploy a component directly on the host instead of within a container, set
the ``is_metal`` property to ``true`` for the container group in the
``container_skel`` section in the appropriate file.

The use of ``container_vars`` and mapping from container groups to host groups
is the same for a service deployed directly onto the host.

You can also use the ``no_containers`` option to specify a host that will have
all services deployed on metal inside of it.

.. note::

   The ``cinder-volume`` component is deployed directly on the host by
   default. See the ``env.d/cinder.yml`` file for this example.

Example: Running all controllers on metal
-----------------------------------------
For example, if you'd like to run all your controllers on metal, you would
have the following inside your ``openstack_user_config.yml``.

   .. code-block:: yaml

     infra_hosts:
       infra1:
         ip: 172.39.123.11
         no_containers: true
       infra2:
         ip: 172.39.123.12
         no_containers: true
       infra3:
         ip: 172.39.123.13
         no_containers: true

Example: Running galera on dedicated hosts
------------------------------------------

For example, to run Galera directly on dedicated hosts, you would perform the
following steps:

#. Modify the ``container_skel`` section of the ``env.d/galera.yml`` file.
   For example:

   .. code-block:: yaml

     container_skel:
       galera_container:
         belongs_to:
           - db_containers
         contains:
           - galera
         properties:
           is_metal: true

   .. note::

      To deploy within containers on these dedicated hosts, omit the
      ``is_metal: true`` property.

#. Assign the ``db_containers`` container group (from the preceding step) to a
   host group by providing a ``physical_skel`` section for the host group
   in a new or existing file, such as ``env.d/galera.yml``.
   For example:

   .. code-block:: yaml

     physical_skel:
       db_containers:
         belongs_to:
           - all_containers
       db_hosts:
         belongs_to:
           - hosts

#. Define the host group (``db_hosts``) in a ``conf.d/`` file (such as
   ``galera.yml``). For example:

   .. code-block:: yaml

     db_hosts:
       db-host1:
         ip: 172.39.123.11
       db-host2:
         ip: 172.39.123.12
       db-host3:
         ip: 172.39.123.13

   .. note::

      Each of the custom group names in this example (``db_containers``
      and ``db_hosts``) are arbitrary. Choose your own group names,
      but ensure the references are consistent among all relevant files.

.. _affinity:

Deploying 0 (or more than one) of component type per host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When OpenStack-Ansible generates its dynamic inventory, the affinity
setting determines how many containers of a similar type are deployed on a
single physical host.

Using ``shared-infra_hosts`` as an example, consider this
``openstack_user_config.yml`` configuration:

.. code-block:: yaml

    shared-infra_hosts:
      infra1:
        ip: 172.29.236.101
      infra2:
        ip: 172.29.236.102
      infra3:
        ip: 172.29.236.103

Three hosts are assigned to the `shared-infra_hosts` group,
OpenStack-Ansible ensures that each host runs a single database container,
a single Memcached container, and a single RabbitMQ container. Each host has
an affinity of 1 by default,  which means that each host runs one of each
container type.

If you are deploying a stand-alone Object Storage (swift) environment,
you can skip the deployment of RabbitMQ. If you use this configuration,
your ``openstack_user_config.yml`` file would look as follows:

.. code-block:: yaml

    shared-infra_hosts:
      infra1:
        affinity:
          rabbit_mq_container: 0
        ip: 172.29.236.101
      infra2:
        affinity:
          rabbit_mq_container: 0
        ip: 172.29.236.102
      infra3:
        affinity:
          rabbit_mq_container: 0
        ip: 172.29.236.103

This configuration deploys a Memcached container and a database container
on each host, but no RabbitMQ containers.

Omit a service or component from the deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To omit a component from a deployment, you can use one of several options:

- Remove the ``physical_skel`` link between the container group and
  the host group by deleting the related file located in the ``env.d/``
  directory.
- Do not run the playbook that installs the component.
  Unless you specify the component to run directly on a host by using the
  ``is_metal`` property, a container is created for this component.
- Adjust the :ref:`affinity`
  to 0 for the host group. Similar to the second option listed here, Unless
  you specify the component to run directly on a host by using the ``is_metal``
  property, a container is created for this component.

