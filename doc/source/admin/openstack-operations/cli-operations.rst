Use the command line clients
============================

This section describes some of the more common commands to
use your OpenStack cloud.

Log in to any utility container or install the openstack client on
your machine, and run the following commands:

The **openstack flavor list** command lists the *flavors* that are
available. These are different disk sizes that can be assigned to
images:

.. code::

   $ openstack flavor list
   +-----+-----------+-------+------+-----------+-------+-----------+
   | ID  | Name      |   RAM | Disk | Ephemeral | VCPUs | Is Public |
   +-----+-----------+-------+------+-----------+-------+-----------+
   | 1   | m1.tiny   |   512 |    1 |         0 |     1 | True      |
   | 2   | m1.small  |  2048 |   20 |         0 |     1 | True      |
   | 3   | m1.medium |  4096 |   40 |         0 |     2 | True      |
   | 4   | m1.large  |  8192 |   80 |         0 |     4 | True      |
   | 5   | m1.xlarge | 16384 |  160 |         0 |     8 | True      |
   +-----+-----------+-------+------+-----------+-------+-----------+

The **openstack floating ip list** command lists the currently
available floating IP addresses and the instances they are
associated with:

.. code::

   $ openstack floating ip list
   +------------------+---------------------+------------------+---------+-------------------+---------------+
   | ID               | Floating IP Address | Fixed IP Address | Port    | Floating Network  | Project       |
   +------------------+---------------------+------------------+---------+-------------------+---------------+
   | 0a88589a-ffac... | 192.168.12.7        | None             | None    | d831dac6-028c...  | 32db2ccf2a... |
   +------------------+---------------------+------------------+---------+-------------------+---------------+


For more information about OpenStack client utilities, see these links:

-  `OpenStack API Quick
   Start <https://docs.openstack.org/api-quick-start/index.html>`__

-  `OpenStackClient
   commands <https://docs.openstack.org/python-openstackclient/latest/>`__

-  `Image Service (glance) CLI
   commands <https://docs.openstack.org/glance/latest/cli/index.html>`__

-  `Image Service (glance) CLI command cheat
   sheet <https://docs.openstack.org/python-glanceclient/latest/cli/glance.html>`__

-  `Compute (nova) CLI
   commands <https://docs.openstack.org/nova/latest/cli/index.html>`__

-  `Compute (nova) CLI command cheat
   sheet <https://docs.openstack.org/python-novaclient/latest/cli/nova.html>`__

-  `Networking (neutron) CLI
   commands <https://docs.openstack.org/neutron/latest/cli/index.html>`__

-  `Networking (neutron) CLI command cheat
   sheet <https://docs.openstack.org/python-neutronclient/latest/cli/neutron.html>`__

-  `Block Storage (cinder) CLI commands
   <https://docs.openstack.org/python-cinderclient/latest/user/shell.html>`__

-  `Block Storage (cinder) CLI command cheat
   sheet <https://docs.openstack.org/python-cinderclient/latest/cli/details.html>`__

-  `python-keystoneclient <https://pypi.org/project/python-keystoneclient/>`__

-  `python-glanceclient <https://pypi.org/project/python-glanceclient/>`__

-  `python-novaclient <https://pypi.org/project/python-novaclient/>`__

-  `python-neutronclient <https://pypi.org/project/python-neutronclient/>`__
