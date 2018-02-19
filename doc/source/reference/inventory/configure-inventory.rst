Configuring the inventory
=========================

conf.d
~~~~~~

Common OpenStack services and their configuration are defined by
OpenStack-Ansible in the
``/etc/openstack_deploy/openstack_user_config.yml`` settings file.

Additional services should be defined with a YAML file in
``/etc/openstack_deploy/conf.d``, in order to manage file size.

Affinity
~~~~~~~~

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

env.d
~~~~~

The ``/etc/openstack_deploy/env.d`` directory sources all YAML files into the
deployed environment, allowing a deployer to define additional group mappings.

This directory is used to extend the environment skeleton, or modify the
defaults defined in the ``inventory/env.d`` directory.

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
