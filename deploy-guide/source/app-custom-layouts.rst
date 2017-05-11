================================================
Appendix D: Customizing host and service layouts
================================================

The default layout of containers and services in OpenStack-Ansible (OSA) is
determined by the ``/etc/openstack_deploy/openstack_user_config.yml`` file and
the contents of both the ``/etc/openstack_deploy/conf.d/`` and
``/etc/openstack_deploy/env.d/`` directories. You use these sources to define
the *group* mappings that the playbooks use to target hosts and containers for
roles used in the deploy.

* You define host groups, which gather the target hosts into *inventory
  groups*, through the ``/etc/openstack_deploy/openstack_user_config.yml``
  file and the contents of the ``/etc/openstack_deploy/conf.d/`` directory.

* You define *container groups*, which can map from the service components
  to be deployed up to host groups, through files in the
  ``/etc/openstack_deploy/env.d/`` directory.

To customize the layout of the components for your deployment, modify the
host groups and container groups appropriately before running the installation
playbooks.

Understanding host groups
~~~~~~~~~~~~~~~~~~~~~~~~~

As part of the initial configuration, each target host appears either in the
``/etc/openstack_deploy/openstack_user_config.yml`` file or in files within
the ``/etc/openstack_deploy/conf.d/`` directory. The format used for files in
the ``conf.d/`` directory is identical to the syntax used in the
``openstack_user_config.yml`` file.

In these files, the target hosts are listed under one or more
headings, such as ``shared-infra_hosts`` or ``storage_hosts``, which serve as
Ansible group mappings. These groups map to the physical
hosts.

The ``haproxy.yml.example`` file in the ``conf.d/`` directory provides
a simple example of defining a host group (``haproxy_hosts``) with two hosts
(``infra1`` and ``infra2``).

The ``swift.yml.example`` file provides a more complex example. Here, host
variables for a target host are specified by using the ``container_vars`` key.
OpenStack-Ansible applies all entries under this key as host-specific
variables to any component containers on the specific host.

.. note::

   To manage file size, we recommend that you define new inventory groups,
   particularly for new services, by using a new file in the
   ``conf.d/`` directory.

Understanding container groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additional group mappings are located within files in the
``/etc/openstack_deploy/env.d/`` directory. These groups are treated as
virtual mappings from the host groups (described above) onto the container
groups, that define where each service deploys. By reviewing files within the
``env.d/`` directory, you can begin to see the nesting of groups represented
in the default layout.

For example, the ``shared-infra.yml`` file defines a container group,
``shared- infra_containers``, as a subset of the all_containers inventory
group. The ``shared- infra_containers`` container group is mapped to the
``shared-infra_hosts`` host group. All of the service components in the
``shared-infra_containers`` container group are deployed to each target host
in the ``shared-infra_hosts host`` group.

Within a ``physical_skel`` section, the OpenStack-Ansible dynamic inventory
expects to find a pair of keys. The first key maps to items in the
``container_skel`` section, and the second key maps to the target host groups
(described above) that are responsible for hosting the service component.

To continue the example, the ``memcache.yml`` file defines the
``memcache_container`` container group. This group is a subset of the
``shared-infra_containers`` group, which is itself a subset of
the ``all_containers`` inventory group.

.. note::

   The ``all_containers`` group is automatically defined by OpenStack-Ansible.
   Any service component managed by OpenStack-Ansible maps to a subset of the
   ``all_containers`` inventory group, directly or indirectly through
   another intermediate container group.

The default layout does not rely exclusively on groups being subsets of other
groups. The ``memcache`` component group is part of the ``memcache_container``
group, as well as the ``memcache_all`` group and also contains a ``memcached``
component group. If you review the ``playbooks/memcached-install.yml``
playbook, you see that the playbook applies to hosts in the ``memcached``
group. Other services might have more complex deployment needs. They define and
consume inventory container groups differently. Mapping components to several
groups in this way allows flexible targeting of roles and tasks.

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
- Adjust the :deploy_guide:`affinity <app-advanced-config-affinity.html>`
  to 0 for the host group. Similar to the second option listed here, Unless
  you specify the component to run directly on a host by using the``is_metal``
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
