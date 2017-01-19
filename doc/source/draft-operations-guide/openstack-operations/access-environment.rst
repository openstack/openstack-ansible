==========================
Accessing your environment
==========================

Viewing and setting environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To connect to the OpenStack installation using command line clients, you must
set the appropriate environment variables. OpenStack clients use environment
variables to provide the information necessary to authenticate to the cloud.
Variables can be viewed and downloaded from the Dashboard and set in the
``admin-openrc.sh`` file on the controller node.

#. Log in to the Dashboard as the ``admin`` user.

#. Select the **Compute** tab in the **Project** section of the
   navigation pane, then click **Access & Security**.

#. Select the **API Access** tab, then click the **Download OpenStack RC
   File** button. Save the ``admin-openrc.sh`` file to your local system.

#. Open the ``admin-openrc.sh`` file in a text editor. The file will
   display:

   .. important::

      The ``admin-openrc.sh`` file contains administrative credentials.
      Ensure you take proper precautions to secure the file.

   .. code::

      #!/bin/bash

      # To use an Openstack cloud you need to authenticate against keystone, which
      # returns a **Token** and **Service Catalog**. The catalog contains the
      # endpoint for all services the user/tenant has access to - including nova,
      # glance, keystone, swift.
      #
      # *NOTE*: Using the 2.0 *auth api* does not mean that compute api is 2.0.We
      # will use the 1.1 *compute api*
      export OS_AUTH_URL=http://192.168.0.7:5000/v2.0

      # With the addition of Keystone we have standardized on the term **tenant**
      # as the entity that owns the resources.
      export OS_TENANT_ID=25da08e142e24f55a9b27044bc0bdf4e
      export OS_TENANT_NAME="admin"

      # In addition to the owning entity (tenant), OpenStack stores the entity
      # performing the action as the **user**.
      export OS_USERNAME="admin"

      # With Keystone you pass the keystone password.
      echo "Please enter your OpenStack Password: "
      read -sr OS_PASSWORD_INPUT
      export OS_PASSWORD=$OS_PASSWORD_INPUT

      # If your configuration has multiple regions, we set that information here.
      # OS_REGION_NAME is optional and only valid in certain environments.
      export OS_REGION_NAME="RegionOne"
      # Don't leave a blank variable, unset it if it was empty
      if [ -z "$OS_REGION_NAME" ]; then unset OS_REGION_NAME; fi


#. Add the following environment variables entries to the
   ``admin-openrc.sh`` file to ensure the OpenStack clients connect to
   the correct endpoint type from the service catalog:

   .. code::

      CINDER_ENDPOINT_TYPE=internalURL
      NOVA_ENDPOINT_TYPE=internalURL
      OS_ENDPOINT_TYPE=internalURL

#. Log in to the controller node.

#. Before running commands, source the ``admin-openrc`` file to set
   environment variables. At the command prompt, type:

   .. code::

      $ source admin-openrc


Managing the cloud using the command-line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section describes some of the more common commands to view and
manage the cloud.

Log in to the controller node to run the following commands:

Server list
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
    All logs are available in the ``/var/log/`` directory and its
    subdirectories. The **tail** command shows the most recent entries
    in a specified log file:

    .. code::

       $ tail /var/log/nova/nova.log


See available flavors
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

List images
    The **openstack image list** command lists the currently available
    images:

    .. code::

       $ openstack image list
       +--------------------------+----------------------------+--------+
       |                  ID      |           Name             | Status |
       +--------------------------+----------------------------+--------+
       | 033c0027-[ID truncated]  |        cirros-image        | active |
       | 0ccfc8c4-[ID truncated]  |         My Image 2         | active |
       | 85a0a926-[ID truncated]  |        precise-image       | active |
       +--------------------------+----------------------------+--------+


List floating IP addresses
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


OpenStack client utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack client utilities are a convenient way to interact with
OpenStack from the command line on the workstation, without being logged
in to the controller nodes.

.. NOTE FROM JP TO ADD LATER:
   If we talk about utilities, I suggest we move the CLI utilities section
   above, because it's used already in things above. It makes sense to first
   install them and then use them. I'd in that case I'd mention that they don't
   need to be installed /upgraded again on the utility containers, because
   they already handled by OSA deployment.

Python client utilities are available using the Python Package Index
(PyPI), and can be installed on most Linux systems using these commands:

.. NOTE FROM JP: I'd maybe mention the python-openstackclient first. It should
   be our first citizen in the future.

 .. code::

    # pip install python-PROJECTclient

 .. note::

    The keystone client utility is deprecated. The OpenStackClient
    utility should be used which supports v2 and v3 Identity API.


Upgrade or remove clients
~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade a client, add the **--upgrade** option to the command:

 .. code::

    # pip install --upgrade python-PROJECTclient


To remove a client, run the **pip uninstall** command:

 .. code::

    # pip uninstall python-PROJECTclient


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
