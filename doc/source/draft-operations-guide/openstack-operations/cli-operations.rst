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
       | [ID truncated]   | ExampleImage | active |
       +------------------+--------------+--------+


List services
~~~~~~~~~~~~~

    The :command:`nova service-list` command details the currently running
    services:

    .. code::

       $ nova service-list
       +----+------------------+------------+----------+---------+-------+----------------------------+-----------------+
       | Id | Binary           | Host       | Zone     | Status  | State | Updated_at                 | Disabled Reason |
       +----+------------------+------------+----------+---------+-------+----------------------------+-----------------+
       | 4  | nova-consoleauth | controller | internal | enabled | up    | 2016-12-14T04:06:03.000000 | -               |
       | 5  | nova-scheduler   | controller | internal | enabled | up    | 2016-12-14T04:06:03.000000 | -               |
       | 6  | nova-conductor   | controller | internal | enabled | up    | 2016-12-14T04:05:59.000000 | -               |
       | 9  | nova-compute     | compute    | nova     | enabled | down  | 2016-10-21T02:35:03.000000 | -               |
       +----+------------------+------------+----------+---------+-------+----------------------------+-----------------+


View logs
~~~~~~~~~

    All logs are available in the ``/var/log/`` directory and its
    subdirectories. The **tail** command shows the most recent entries
    in a specified log file:

    .. code::

       $ tail /var/log/nova/nova.log


List flavors
~~~~~~~~~~~~

    The **openstack flavor list** command lists the *flavors* that are
    available. These are different disk sizes that can be assigned to
    images:

    .. code::

       $ nova flavor-list
       +----+-----------+-----------+------+-----------+------+-------+-------------+
       | ID |    Name   | Memory_MB | Disk | Ephemeral | Swap | VCPUs | RXTX_Factor |
       +----+-----------+-----------+------+-----------+------+-------+-------------+
       | 1  | m1.tiny   | 512       | 0    | 0         |      | 1     | 1.0         |
       | 2  | m1.small  | 2048      | 10   | 20        |      | 1     | 1.0         |
       | 3  | m1.medium | 4096      | 10   | 40        |      | 2     | 1.0         |
       | 4  | m1.large  | 8192      | 10   | 80        |      | 4     | 1.0         |
       | 5  | m1.xlarge | 16384     | 10   | 160       |      | 8     | 1.0         |
       +----+-----------+-----------+------+-----------+------+-------+-------------+


    .. important::

       Do not remove the default flavors.

List floating IP addresses
~~~~~~~~~~~~~~~~~~~~~~~~~~

    The **openstack floating ip list** command lists the currently
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
   Start <http://developer.openstack.org/api-guide/quick-start/index.html>`__

-  `OpenStackClient
   commands <http://docs.openstack.org/developer/python-openstackclient/command-list.html>`__

-  `Image Service (glance) CLI
   commands <http://docs.openstack.org/cli-reference/glance.html>`__

-  `Image Service (glance) CLI command cheat
   sheet <http://docs.openstack.org/user-guide/cli-cheat-sheet.html#images-glance>`__

-  `Compute (nova) CLI
   commands <http://docs.openstack.org/cli-reference/nova.html>`__

-  `Compute (nova) CLI command cheat
   sheet <http://docs.openstack.org/user-guide/cli-cheat-sheet.html#compute-nova>`__

-  `Networking (neutron) CLI
   commands <http://docs.openstack.org/cli-reference/neutron.html>`__

-  `Networking (neutron) CLI command cheat
   sheet <http://docs.openstack.org/user-guide/cli-cheat-sheet.html#networking-neutron>`__

-  `Block Storage (cinder) CLI commands
   <http://docs.openstack.org/cli-reference/cinder.html>`__

-  `Block Storage (cinder) CLI command cheat
   sheet <http://docs.openstack.org/user-guide/cli-cheat-sheet.html#block-storage-cinder>`__

-  `python-keystoneclient <https://pypi.python.org/pypi/python-keystoneclient/>`__

-  `python-glanceclient <https://pypi.python.org/pypi/python-glanceclient/>`__

-  `python-novaclient <https://pypi.python.org/pypi/python-novaclient/>`__

-  `python-neutronclient <https://pypi.python.org/pypi/python-neutronclient/>`__
