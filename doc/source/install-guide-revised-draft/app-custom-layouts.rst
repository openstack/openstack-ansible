`Home <index.html>`_ OpenStack-Ansible Installation Guide

==================================================
Appendix E: Customizing host and service layouts
==================================================

Understanding the default layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default layout of containers and services in OpenStack-Ansible is driven
by the ``/etc/openstack_deploy/openstack_user_config.yml`` file and the
contents of both the ``/etc/openstack_deploy/conf.d/`` and
``/etc/openstack_deploy/env.d/`` directories. Use these sources to define the
group mappings used by the playbooks to target hosts and containers for roles
used in the deploy.

Conceptually, these can be thought of as mapping from two directions. You
define host groups, which gather the target hosts into inventory groups,
through the ``/etc/openstack_deploy/openstack_user_config.yml`` file and the
contents of the ``/etc/openstack_deploy/conf.d/`` directory. You define
container groups, which can map from the service components to be deployed up
to host groups, through files in the ``/etc/openstack_deploy/env.d/``
directory.

To customize the layout of components for your deployment, modify the
host groups and container groups appropriately to represent the layout you
desire before running the installation playbooks.

Understanding host groups
-------------------------
As part of initial configuration, each target host appears in either the
``/etc/openstack_deploy/openstack_user_config.yml`` file or in files within
the ``/etc/openstack_deploy/conf.d/`` directory. We use a format for files in
``conf.d/`` which is identical to the syntax used in the
``openstack_user_config.yml`` file. These hosts are listed under one or more
headings such as ``shared-infra_hosts`` or ``storage_hosts`` which serve as
Ansible group mappings. We treat these groupings as mappings to the physical
hosts.

The example file ``haproxy.yml.example`` in the ``conf.d/`` directory provides
a simple example of defining a host group (``haproxy_hosts``) with two hosts
(``infra1`` and ``infra2``).

A more complex example file is ``swift.yml.example``. Here, in addition, we
specify host variables for a target host using the ``container_vars`` key.
OpenStack-Ansible applies all entries under this key as host-specific
variables to any component containers on the specific host.

.. note::

   Our current recommendation is for new inventory groups, particularly for new
   services, to be defined using a new file in the ``conf.d/`` directory in
   order to manage file size.

Understanding container groups
------------------------------
Additional group mappings can be found within files in the
``/etc/openstack_deploy/env.d/`` directory. These groupings are treated as
virtual mappings from the host groups (described above) onto the container
groups which define where each service deploys. By reviewing files within the
``env.d/`` directory, you can begin to see the nesting of groups represented
in the default layout.

We begin our review with ``shared-infra.yml``. In this file we define a
new container group (``shared-infra_containers``) as a subset of the
``all_containers`` group. This new container group is mapped to a new
(``shared-infra_hosts``) host group. This means you deploy all service
components under the new (``shared-infra_containers``) container group to each
target host in the host group (``shared-infra_hosts``).

Within a ``physical_skel`` segment, the OpenStack-Ansible dynamic inventory
expects to find a pair of keys. The first key maps to items in the
``container_skel`` and the second key maps to the target host groups
(described above) which are responsible for hosting the service component.

Next, we review ``memcache.yml``. Here, we define the new group
``memcache_container``. In this case we identify the new group as a
subset of the ``shared-infra_containers`` group, which is itself a subset of
the ``all_containers`` inventory group.

.. note::

   The ``all_containers`` group is automatically defined by OpenStack-Ansible.
   Any service component managed by OpenStack-Ansible maps to a subset of the
   ``all_containers`` inventory group, whether directly or indirectly through
   another intermediate container group.

The default layout does not rely exclusively on groups being subsets of other
groups. The ``memcache`` component group is part of the ``memcache_container``
group, as well as the ``memcache_all`` group and also contains a ``memcached``
component group. If you review the ``playbooks/memcached-install.yml``
playbook you see that the playbook applies to hosts in the ``memcached``
group. Other services may have more complex deployment needs. They define and
consume inventory container groups differently. Mapping components to several
groups in this way allows flexible targeting of roles and tasks.

Customizing existing components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Numerous customization scenarios are possible, but three popular ones are
presented here as starting points and also as common recipes.

Deploying directly on hosts
---------------------------

To deploy a component directly on the host instead of within a container, set
the ``is_metal`` property to ``true`` for the container group under the
``container_skel`` in the appropriate file.

The use of ``container_vars`` and mapping from container groups to host groups
is the same for a service deployed directly onto the host.

.. note::

   The ``cinder_volume`` component is also deployed directly on the host by
   default. See the ``env.d/cinder.yml`` file for this example.

Omit a service or component from the deployment
-----------------------------------------------

To omit a component from a deployment, several options exist.

- You could remove the ``physical_skel`` link between the container group and
  the host group. The simplest way to do this is to simply delete the related
  file located in the ``env.d/`` directory.
- You could choose to not run the playbook which installs the component.
  Unless you specify the component to run directly on a host using is_metal, a
  container creates for this component.
- You could adjust the ``affinity`` to 0 for the host group. Unless you
  specify the component to run directly on a host using is_metal, a container
  creates for this component. `Affinity`_ is discussed in the initial
  environment configuration section of the install guide.

.. _Affinity: configure-initial.html#affinity

Deploying existing components on dedicated hosts
------------------------------------------------

To deploy a shared-infra component onto dedicated hosts, modify both the
files specifying the host groups and container groups for the component.

For example, to run Galera directly on dedicated hosts the ``container_skel``
segment of the ``env.d/galera.yml`` file might look like:

.. code-block:: yaml

    container_skel:
      galera_container:
        belongs_to:
          - db_containers
        contains:
          - galera
        properties:
          log_directory: mysql_logs
          service_name: galera
          is_metal: true

.. note::

   If you want to deploy within containers on these dedicated hosts, omit the
   ``is_metal: true`` property. We include it here as a recipe for the more
   commonly requested layout.

Since we define the new container group (``db_containers`` above) we must
assign that container group to a host group. To assign the new container
group to a new host group, provide a ``physical_skel`` for the new host group
(in a new or existing file, such as ``env.d/galera.yml``) like the following:

.. code-block:: yaml

    physical_skel:
      db_containers:
        belongs_to:
          - all_containers
      db_hosts:
        belongs_to:
          - hosts

Lastly, define the host group (db_hosts above) in a ``conf.d/`` file (such as
``galera.yml``).

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
   and ``db_hosts``) were arbitrary. You can choose your own group names
   but be sure the references are consistent between all relevant files.
