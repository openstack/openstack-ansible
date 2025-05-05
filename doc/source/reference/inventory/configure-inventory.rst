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

   Never edit or delete the file
   ``/etc/openstack_deploy/openstack_inventory.json``. This can lead to
   problems with the inventory: existng hosts and containers will be unmanaged
   and new ones will be generated instead, breaking your existing deployment.

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

Example: Running Galera on dedicated hosts
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

Adding virtual nest groups
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to create a custom group for arbitrary grouping of hosts and
containers within these hosts but skip the generation of any new containers,
you should use ``is_nest`` property under container_skel and skip defining
``belongs_to`` structure. ``is_nest`` property will add host-containers as
children to such a group.

Example: Defining Availability Zones
------------------------------------

A good example of how ``is_nest`` property can be used is describing
Availability Zones. As when operating multiple AZs it's handy to define
AZ-specific variables, like AZ name, for all hosts in this AZ. And
leveraging ``group_vars`` is best way of ensuring that all hosts that belong
to same AZ have same configuration applied.

Let's assume you have 3 controllers and each of them is placed
in different Availability Zones. There is also a compute node in
each Availability Zone. And we want each host or container that is placed
physically in a specific AZ be part of it's own group (ie ``azN_all``)

In order to achieve that we need:

#. Define host groups in ``conf.d`` or ``openstack_user_config.yml`` to assign hosts
   accordingly to their Availability Zones:

   .. code-block:: yaml

     az1-infra_hosts: &infra_az1
       az1-infra1:
         ip: 172.39.123.11

     az2-infra_hosts: &infra_az2
       az2-infra2:
         ip: 172.39.123.12

     az3-infra_hosts: &infra_az3
       az3-infra3:
         ip: 172.39.123.13

     shared-infra_hosts: &controllers
       <<: *infra_az1
       <<: *infra_az2
       <<: *infra_az3

     az1-compute_hosts: &computes_az1
       az1-compute01:
         ip: 172.39.123.100

     az2-compute_hosts: &computes_az2
       az2-compute01:
         ip: 172.39.123.150

     az3-compute_hosts: &computes_az3
       az3-compute01:
         ip: 172.39.123.200

     compute_hosts:
       <<: *computes_az1
       <<: *computes_az2
       <<: *computes_az3

     az1_hosts:
       <<: *computes_az1
       <<: *infra_az1

     az2_hosts:
       <<: *computes_az2
       <<: *infra_az2

     az3_hosts:
       <<: *computes_az3
       <<: *infra_az3

#. Create ``env.d/az.yml`` file that will leverage ``is_nest`` property and allow
   all infra containers to be part of the AZ group as well

   .. code-block:: yaml

     component_skel:
       az1_containers:
         belongs_to:
           - az1_all
       az1_hosts:
         belongs_to:
           - az1_all

       az2_containers:
         belongs_to:
           - az2_all
       az2_hosts:
         belongs_to:
           - az2_all

       az3_containers:
         belongs_to:
           - az3_all
       az3_hosts:
         belongs_to:
           - az3_all

     container_skel:
       az1_containers:
         properties:
           is_nest: True
       az2_containers:
         properties:
           is_nest: True
       az3_containers:
         properties:
           is_nest: True

#. Now you can leverage ``group_vars`` file to apply a variable to all
   containers and bare metal hosts in AZ.
   For example ``/etc/openstack_deploy/group_vars/az1_all.yml``:

   .. code-block:: yaml

     ---
     az_name: az1
     cinder_storage_availability_zone: "{{ az_name }}"


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

Three hosts are assigned to the ``shared-infra_hosts`` group,
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


Having SSH network different from OpenStack Management network
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some environments SSH network that is used to access nodes from deploy
host and management network are different. In this case it's important that
services were listening on correct network while ensure that Ansible use SSH
network for accessing managed hosts. In these cases you can define
``management_ip`` key while defining hosts in your ``openstack_user_config.yml``
file.

``management_ip`` will be used as ``management_address`` for the node, while
``ip`` will be used as ``ansible_host`` for accessing node by SSH.

Example:

.. code-block:: yaml

    shared-infra_hosts:
      infra1:
        ip: 192.168.0.101
        management_ip: 172.29.236.101
