=========================
Configuring the inventory
=========================

Changing the base environment directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--environment/-e`` argument will take the path to a directory containing
an ``env.d`` directory. This defaults to ``playbooks/inventory/`` in the
OpenStack-Ansible codebase.

Contents of this directory are populated into the environment *before* the
``env.d`` found in the directory specified by ``--config``.


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

Dynamic Inventory API documentation
-----------------------------------

.. automodule:: dynamic_inventory
   :members:

