.. _developer-inventory:

===========================
OpenStack-Ansible Inventory
===========================

OpenStack-Ansible uses an included script to generate the inventory of hosts
and containers within the environment. This script is called by Ansible
through its `dynamic inventory functionality`_.


Generating the Inventory
------------------------

The script that creates the inventory is located at
``playbooks/inventory/dynamic_inventory.py``.

Execution
^^^^^^^^^

When running an Ansible command (such as ``ansible``, ``ansible-playbook`` or
``openstack-ansible``) Ansible will execute the ``dynamic_inventory.py`` script
and use its output as inventory.

The command can also be run manually as follows:

.. code-block:: bash

    # from the playbooks directory
    inventory/dynamic_inventory.py --config /etc/openstack_deploy/

This invocation is useful when testing changes to the dynamic inventory script.

.. note:: When running the ``dynamic_inventory.py`` script on a local
          development machine, use ``python dynamic_inventory.py`` instead.

Inputs
^^^^^^

The ``dynamic_inventory.py`` takes the ``--config`` argument for the directory
holding configuration from which to create the inventory. If not specified,
the default is ``/etc/openstack_deploy/``.

In addition to this argument, the base environment skeleton is provided in the
``playbooks/inventory/env.d`` directory of the OpenStack-Ansible codebase.

Should an ``env.d`` directory be found in the directory specified by
``--config``, its contents will be added to the base environment, overriding
any previous contents in the event of conflicts.

.. note:: In all versions prior to |previous_release_formal_name|, this argument was ``--file``.

The following file must be present in the configuration directory:

* ``openstack_user_config.yml``

Additionally, the configuration or environment could be spread between two
additional sub-directories:

* ``conf.d``
* ``env.d`` (for environment customization)

The dynamic inventory script does the following:

* Generates the names of each container that runs a service
* Creates container and IP address mappings
* Assigns containers to physical hosts

As an example, consider the following excerpt from
``openstack_user_config.yml``:

.. code-block :: yaml

    identity_hosts:
      infra01:
        ip: 10.0.0.10
      infra02:
        ip: 10.0.0.11
      infra03:
        ip: 10.0.0.12

The ``identity_hosts`` dictionary defines an Ansible inventory group named
``identity_hosts`` containing the three infra hosts. The configuration file
``playbooks/inventory/env.d/keystone.yml`` defines additional Ansible
inventory groups for the containers that are deployed onto the three hosts
named with the prefix *infra*.

Note that any services marked with ``is_metal: true`` will run on the allocated
physical host and not in a container. For an example of ``is_metal: true``
being used refer to ``playbooks/inventory/env.d/cinder.yml`` in the
``container_skel`` section.

Outputs
^^^^^^^

Once executed, the script will output an ``openstack_inventory.json`` file into
the directory specified with the ``--config`` argument. This is used as the
source of truth for repeated runs.

.. note::
    The ``openstack_inventory.json`` file is the source of truth for the
    environment. Deleting this in a production environment means that the UUID
    portion of container names will be regenerated, which then results in new
    containers being created. Containers generated under the previous version
    will no longer be recognized by Ansible, even if reachable via SSH.

The same JSON structure is printed to stdout, which is consumed by Ansible as
the inventory for the playbooks.


Changing the Base Environment Directory
---------------------------------------

The ``--environment/-e`` argument will take the path to a directory containing
an ``env.d`` directory. This defaults to ``playbooks/inventory/`` in the
OpenStack-Ansible codebase.

Contents of this directory are populated into the environment *before* the
``env.d`` found in the directory specified by ``--config``.


Checking Inventory Configuration for Errors
-------------------------------------------

Using the ``--check`` flag when running ``dynamic_inventory.py`` will run the
inventory build process and look for known errors, but not write any files to
disk.

If any groups defined in the ``openstack_user_config.yml`` or ``conf.d`` files
are not found in the environment, a warning will be raised.

This check does not do YAML syntax validation, though it will fail if there
are unparseable errors.

Writing Debug Logs
------------------

The ``--debug/-d`` parameter allows writing of a detailed log file for
debugging the inventory script's behavior. The output is written to
``inventory.log`` in the current working directory.

The ``inventory.log`` file is appended to, not overwritten.

Like ``--check``, this flag is not invoked when running from ansible.

Inspecting and Managing the Inventory
-------------------------------------

The file ``scripts/inventory-manage.py`` is used to produce human readable
output based on the ``/etc/openstack_deploy/openstack_inventory.json`` file.

The same script can be used to safely remove hosts from the inventory, export
the inventory based on hosts, and clear IP addresses from containers within
the inventory files.

Operations taken by this script only affect the
``/etc/opentstack_deploy/openstack_inventory.json`` file; any new or removed
information must be set by running playbooks.

Viewing the Inventory
^^^^^^^^^^^^^^^^^^^^^

The ``/etc/openstack_deploy/openstack_inventory.json`` file is read by default.
An alternative file can be specified with ``--file``.

A list of all hosts can be seen with the ``--list-host/-l`` argument

To see a listing of hosts and containers by their group, use
``--list-groups/-g``.

To see all of the containers, use ``--list-containers/-G``.

Removing a Host
^^^^^^^^^^^^^^^

A host can be removed with the ``--remove-item/-r`` parameter.

Use the host's name as an argument.

..  _`dynamic inventory functionality`: http://docs.ansible.com/ansible/intro_dynamic_inventory.html

Exporting Host Information
^^^^^^^^^^^^^^^^^^^^^^^^^^

Information on a per-host basis can be obtained with the ``--export/-e``
parameter.

This JSON output has two top-level keys: ``hosts`` and ``all``.

``hosts`` contains a map of a host's name to its variable and group data.

``all`` contains global network information such as the load balancer IPs and
provider network metadata.

Clearing Existing Container IP Addresses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``--clear-ips`` parameter can be used to remove all container IP address
information from the ``openstack_inventory.json`` file. Baremetal hosts will
not be changed.

This will *not* change the LXC configuration until the associated playbooks
are run and the containers restarted, which will result in API downtime.

Any changes to the containers must also be reflected in the deployment's load
balancer.

The lxc_hosts Group
-------------------

When a container name is created by the dynamic inventory script, the host on
which the container resides is added to the ``lxc_hosts`` inventory group.

Using this name for a group in the configuration will result in a runtime
error.

Dynamic Inventory API documentation
-----------------------------------

.. automodule:: dynamic_inventory
   :members:
