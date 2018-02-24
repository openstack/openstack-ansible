.. _configuring-inventory:

Configuring the inventory
=========================

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

Customizing existing components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploying directly on hosts
---------------------------

To deploy a component directly on the host instead of within a container, set
the ``is_metal`` property to ``true`` for the container group in the
``container_skel`` section in the appropriate file.

The use of ``container_vars`` and mapping from container groups to host groups
is the same for a service deployed directly onto the host.

.. note::

   The ``cinder-volume`` component is deployed directly on the host by
   default. See the ``env.d/cinder.yml`` file for this example.

Omit a service or component from the deployment
-----------------------------------------------

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

Deploy existing components on dedicated hosts
---------------------------------------------

To deploy a ``shared-infra`` component to dedicated hosts, modify the
files that specify the host groups and container groups for the component.

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


Checking inventory configuration for errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the ``--check`` flag when running ``dynamic_inventory.py`` will run the
inventory build process and look for known errors, but not write any files to
disk.

If any groups defined in the ``openstack_user_config.yml`` or ``conf.d`` files
are not found in the environment, a warning will be raised.

This check does not do YAML syntax validation, though it will fail if there
are unparseable errors.

Writing debug logs
~~~~~~~~~~~~~~~~~~~

The ``--debug/-d`` parameter allows writing of a detailed log file for
debugging the inventory script's behavior. The output is written to
``inventory.log`` in the current working directory.

The ``inventory.log`` file is appended to, not overwritten.

Like ``--check``, this flag is not invoked when running from ansible.
