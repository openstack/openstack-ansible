=====================================
Inspecting and managing the inventory
=====================================

The file ``scripts/inventory-manage.py`` is used to produce human readable
output based on the ``/etc/openstack_deploy/openstack_inventory.json`` file.

The same script can be used to safely remove hosts from the inventory, export
the inventory based on hosts, and clear IP addresses from containers within
the inventory files.

Operations taken by this script only affect the
``/etc/opentstack_deploy/openstack_inventory.json`` file; any new or removed
information must be set by running playbooks.

Viewing the inventory
~~~~~~~~~~~~~~~~~~~~~

The ``/etc/openstack_deploy/openstack_inventory.json`` file is read by default.
An alternative file can be specified with ``--file``.

A list of all hosts can be seen with the ``--list-host/-l`` argument

To see a listing of hosts and containers by their group, use
``--list-groups/-g``.

To see all of the containers, use ``--list-containers/-G``.

Removing a host
~~~~~~~~~~~~~~~

A host can be removed with the ``--remove-item/-r`` parameter.

Use the host's name as an argument.

..  _`dynamic inventory functionality`: http://docs.ansible.com/ansible/intro_dynamic_inventory.html

Exporting host information
~~~~~~~~~~~~~~~~~~~~~~~~~~

Information on a per-host basis can be obtained with the ``--export/-e``
parameter.

This JSON output has two top-level keys: ``hosts`` and ``all``.

``hosts`` contains a map of a host's name to its variable and group data.

``all`` contains global network information such as the load balancer IPs and
provider network metadata.

Clearing existing container IP addresses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--clear-ips`` parameter can be used to remove all container IP address
information from the ``openstack_inventory.json`` file. Baremetal hosts will
not be changed.

This will *not* change the LXC configuration until the associated playbooks
are run and the containers restarted, which will result in API downtime.

Any changes to the containers must also be reflected in the deployment's load
balancer.
