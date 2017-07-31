=========================================
Managing the cloud using the command line
=========================================

This section describes some of the more common commands to view and
manage the cloud.

Log in to any utility container to run the following commands:

List images
~~~~~~~~~~~

The :command:`openstack image list` command shows details about currently
available images:

.. code::

   $ openstack image list
   +------------------+--------------+--------+
   |         ID       |    Name      | Status |
   +------------------+--------------+--------+
   | [ID truncated]   | ExaeImage | active |
   +------------------+--------------+--------+


List compute services
~~~~~~~~~~~~~~~~~~~~~

The :command:`openstack compute service list` command details the currently
running compute services:

.. code::

   $ openstack compute service list
   +------------------+------------+----------+---------+-------+----------------------------+
   | Binary           | Host       | Zone     | Status  | State | Updated_at                 |
   +------------------+------------+----------+---------+-------+----------------------------+
   | nova-consoleauth | controller | internal | enabled | up    | 2017-02-21T20:25:17.000000 |
   | nova-scheduler   | controller | internal | enabled | up    | 2017-02-21T20:25:18.000000 |
   | nova-conductor   | controller | internal | enabled | up    | 2017-02-21T20:25:20.000000 |
   | nova-compute     | compute    | nova     | enabled | up    | 2017-02-21T20:25:20.000000 |
   +------------------+------------+----------+---------+-------+----------------------------+


List flavors
~~~~~~~~~~~~

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


List floating IP addresses
~~~~~~~~~~~~~~~~~~~~~~~~~~

he **openstack floating ip list** command lists the currently
available floating IP addresses and the instances they are
associated with:

.. code::

   $ openstack floating ip list
   +------------------+------------------+---------------------+------------ +
   | id               | fixed_ip_address | floating_ip_address | port_id     |
   +------------------+------------------+---------------------+-------------+
   | 0a88589a-ffac... |                  | 208.113.177.100     |             |
   +------------------+------------------+---------------------+-------------+


For more information about OpenStack client utilities, see these links:

-  `OpenStack API Quick
   Start <https://developer.openstack.org/api-guide/quick-start/index.html>`__

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
   <https://docs.openstack.org/python-cinderclient/latest/user/cinder.html>`__

-  `Block Storage (cinder) CLI command cheat
   sheet <https://docs.openstack.org/python-cinderclient/latest/cli/details.html>`__

-  `python-keystoneclient <https://pypi.python.org/pypi/python-keystoneclient/>`__

-  `python-glanceclient <https://pypi.python.org/pypi/python-glanceclient/>`__

-  `python-novaclient <https://pypi.python.org/pypi/python-novaclient/>`__

-  `python-neutronclient <https://pypi.python.org/pypi/python-neutronclient/>`__
