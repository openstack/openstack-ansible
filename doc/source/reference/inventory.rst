========================
Generating the Inventory
========================

The script that creates the inventory is located at
``playbooks/inventory/dynamic_inventory.py``.

Executing the dynamic_inventory.py script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running an Ansible command (such as ``ansible``, ``ansible-playbook`` or
``openstack-ansible``) Ansible executes the ``dynamic_inventory.py`` script
and use its output as inventory.

Run the following command:

.. code-block:: bash

    # from the playbooks directory
    inventory/dynamic_inventory.py --config /etc/openstack_deploy/

This invocation is useful when testing changes to the dynamic inventory script.

Inputs
~~~~~~

The ``dynamic_inventory.py`` takes the ``--config`` argument for the directory
holding configuration from which to create the inventory. If not specified,
the default is ``/etc/openstack_deploy/``.

In addition to this argument, the base environment skeleton is provided in the
``playbooks/inventory/env.d`` directory of the OpenStack-Ansible codebase.

Should an ``env.d`` directory be found in the directory specified by
``--config``, its contents will be added to the base environment, overriding
any previous contents in the event of conflicts.

.. note::

   In all versions prior to |previous_release_formal_name|, this argument was ``--file``.

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
