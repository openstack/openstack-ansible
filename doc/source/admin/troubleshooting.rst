===============
Troubleshooting
===============

This chapter is intended to help troubleshoot and resolve operational issues in
an OpenStack-Ansible deployment.

Networking
~~~~~~~~~~

This section focuses on troubleshooting general host-to-host communication
required for the OpenStack control plane to function properly.

This does not cover any networking related to instance connectivity.

These instructions assume an OpenStack-Ansible installation using LXC
containers, VXLAN overlay for ML2/OVS and Geneve overlay for the ML2/OVN drivers.

Network List
------------

1. ``HOST_NET`` (Physical Host Management and Access to Internet)
2. ``MANAGEMENT_NET`` (LXC container network used OpenStack Services)
3. ``OVERLAY_NET`` (VXLAN overlay network for OVS, Geneve overlay network for OVN)

Useful network utilities and commands:

.. code-block:: console

   # ip link show [dev INTERFACE_NAME]
   # arp -n [-i INTERFACE_NAME]
   # ip [-4 | -6] address show [dev INTERFACE_NAME]
   # ping <TARGET_IP_ADDRESS>
   # tcpdump [-n -nn] < -i INTERFACE_NAME > [host SOURCE_IP_ADDRESS]
   # brctl show [BRIDGE_ID]
   # iptables -nL
   # arping [-c NUMBER] [-d] <TARGET_IP_ADDRESS>

Troubleshooting host-to-host traffic on HOST_NET
------------------------------------------------

Perform the following checks:

- Check physical connectivity of hosts to physical network
- Check interface bonding (if applicable)
- Check VLAN configurations and any necessary trunking to edge ports
  on physical switch
- Check VLAN configurations and any necessary trunking to uplink ports
  on physical switches (if applicable)
- Check that hosts are in the same IP subnet
  or have proper routing between them
- Check there are no iptables applied to the hosts that would deny traffic

IP addresses should be applied to physical interface, bond interface,
tagged sub-interface, or in some cases the bridge interface:

.. code-block:: console

   # ip address show dev bond0
   14: bond0: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500..UP...
   link/ether a0:a0:a0:a0:a0:01 brd ff:ff:ff:ff:ff:ff
   inet 10.240.0.44/22 brd 10.240.3.255 scope global bond0
      valid_lft forever preferred_lft forever
   ...

Troubleshooting host-to-host traffic on MANAGEMENT_NET
------------------------------------------------------

Perform the following checks:

- Check physical connectivity of hosts to physical network
- Check interface bonding (if applicable)
- Check VLAN configurations and any necessary trunking to edge ports on
  physical switch
- Check VLAN configurations and any necessary trunking to uplink ports
  on physical switches (if applicable)
- Check that hosts are in the same subnet or have proper routing between them
- Check there are no iptables applied to the hosts that would deny traffic
- Check to verify that physical interface is in the bridge
- Check to verify that veth-pair end from container is in ``br-mgmt``

IP address should be applied to ``br-mgmt``:

.. code-block:: console

   # ip address show dev br-mgmt
   18: br-mgmt: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500...UP...
   link/ether a0:a0:a0:a0:a0:01 brd ff:ff:ff:ff:ff:ff
   inet 172.29.236.44/22 brd 172.29.239.255 scope global br-mgmt
      valid_lft forever preferred_lft forever
   ...

IP address should be applied to ``eth1`` inside the LXC container:

.. code-block:: console

   # ip address show dev eth1
   59: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500...UP...
   link/ether b1:b1:b1:b1:b1:01 brd ff:ff:ff:ff:ff:ff
   inet 172.29.236.55/22 brd 172.29.239.255 scope global eth1
      valid_lft forever preferred_lft forever
      ...

``br-mgmt`` should contain veth-pair ends from all containers and a
physical interface or tagged-subinterface:

.. code-block:: console

   # brctl show br-mgmt
   bridge name bridge id          STP enabled  interfaces
   br-mgmt     8000.abcdef12345   no           11111111_eth1
                                               22222222_eth1
                                               ...
                                               bond0.100
                                               99999999_eth1
                                               ...

You can also use ip command to display bridges:

.. code-block:: console

   # ip link show master br-mgmt

   12: bond0.100@bond0: ... master br-mgmt state UP mode DEFAULT group default qlen 1000
   ....
   51: 11111111_eth1_eth1@if3: ... master br-mgmt state UP mode DEFAULT group default qlen 1000
   ....

Troubleshooting host-to-host traffic on OVERLAY_NET
---------------------------------------------------

Perform the following checks:

- Check physical connectivity of hosts to physical network
- Check interface bonding (if applicable)
- Check VLAN configurations and any necessary trunking to edge ports
  on physical switch
- Check VLAN configurations and any necessary trunking to uplink ports
  on physical switches (if applicable)
- Check that hosts are in the same subnet or have proper routing between them
- Check there are no iptables applied to the hosts that would deny traffic
- Check to verify that physcial interface is in the bridge
- Check to verify that veth-pair end from container is in ``br-vxlan``

IP address should be applied to ``br-vxlan``:

.. code-block:: console

   # ip address show dev br-vxlan
   21: br-vxlan: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500...UP...
   link/ether a0:a0:a0:a0:a0:02 brd ff:ff:ff:ff:ff:ff
   inet 172.29.240.44/22 brd 172.29.243.255 scope global br-vxlan
      valid_lft forever preferred_lft forever
      ...

Checking services
~~~~~~~~~~~~~~~~~

You can check the status of an OpenStack service by accessing every controller
node and running the :command:`systemctl status <SERVICE_NAME>`.

See the following links for additional information to verify OpenStack
services:

- `Identity service (keystone) <https://docs.openstack.org/keystone/latest/install/keystone-verify-ubuntu.html>`_
- `Image service (glance) <https://docs.openstack.org/glance/latest/install/verify.html>`_
- `Compute service (nova) <https://docs.openstack.org/nova/latest/install/verify.html>`_
- `Networking service (neutron) <https://docs.openstack.org/neutron/latest/install/verify.html>`_
- `Block Storage service (cinder) <https://docs.openstack.org/cinder/latest/install/cinder-verify.html>`_
- `Object Storage service (swift) <https://docs.openstack.org/swift/latest/install/verify.html>`_

Some useful commands to manage LXC see :ref:`command-line-reference`.

Restarting services
~~~~~~~~~~~~~~~~~~~

Restart your OpenStack services by accessing every controller node. Some
OpenStack services will require restart from other nodes in your environment.

The following table lists the commands to restart an OpenStack service.

.. list-table:: Restarting OpenStack services
   :widths: 30 70
   :header-rows: 1

   * - OpenStack service
     - Commands

   * - Image service
     - .. code-block:: console

          # systemctl restart glance-api

   * - Compute service (controller node)
     - .. code-block:: console

          # systemctl restart nova-api-os-compute
          # systemctl restart nova-scheduler
          # systemctl restart nova-conductor
          # systemctl restart nova-api-metadata
          # systemctl restart nova-novncproxy (if using noVNC)
          # systemctl restart nova-spicehtml5proxy (if using SPICE)

   * - Compute service (compute node)
     - .. code-block:: console

          # systemctl restart nova-compute

   * - Networking service (controller node, for OVS)
     - .. code-block:: console

          # systemctl restart neutron-server
          # systemctl restart neutron-dhcp-agent
          # systemctl restart neutron-l3-agent
          # systemctl restart neutron-metadata-agent
          # systemctl restart neutron-openvswitch-agent

   * - Networking service (compute node)
     - .. code-block:: console

          # systemctl restart neutron-openvswitch-agent

   * - Networking service (controller node, for OVN)
     - .. code-block:: console

          # systemctl restart neutron-server
          # systemctl restart neutron-ovn-maintenance-worker
          # systemctl restart neutron-periodic-workers

   * - Networking service (compute node, for OVN)
     - .. code-block:: console

          # systemctl restart neutron-ovn-metadata-agent

   * - Block Storage service
     - .. code-block:: console

          # systemctl restart cinder-api
          # systemctl restart cinder-backup
          # systemctl restart cinder-scheduler
          # systemctl restart cinder-volume

   * - Shared Filesystems service
     - .. code-block:: console

          # systemctl restart manila-api
          # systemctl restart manila-data
          # systemctl restart manila-share
          # systemctl restart manila-scheduler

   * - Object Storage service
     - .. code-block:: console

          # systemctl restart swift-account-auditor
          # systemctl restart swift-account-server
          # systemctl restart swift-account-reaper
          # systemctl restart swift-account-replicator
          # systemctl restart swift-container-auditor
          # systemctl restart swift-container-server
          # systemctl restart swift-container-reconciler
          # systemctl restart swift-container-replicator
          # systemctl restart swift-container-sync
          # systemctl restart swift-container-updater
          # systemctl restart swift-object-auditor
          # systemctl restart swift-object-expirer
          # systemctl restart swift-object-server
          # systemctl restart swift-object-reconstructor
          # systemctl restart swift-object-replicator
          # systemctl restart swift-object-updater
          # systemctl restart swift-proxy-server

Troubleshooting instance connectivity issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section will focus on troubleshooting general instances
connectivity communication. This does not cover any networking related
to instance connectivity. This is assuming a OpenStack-Ansible install using LXC
containers, VXLAN overlay for ML2/OVS and Geneve overlay for the ML2/OVN driver.

**Data flow example (for OVS)**

.. code-block:: console

   COMPUTE NODE
                                                  +-------------+    +-------------+
                                  +->"If VXLAN"+->+  *br vxlan  +--->+  bond0.#00  +---+
                                  |               +-------------+    +-------------+   |
                   +-------------+                                                      |   +-----------------+
   Instance +--->  | qbr bridge  |++                                                    +-->| physical network|
                   +-------------+                                                      |   +-----------------+
                                  |               +-------------+    +-------------+   |
                                  +->"If  VLAN"+->+   br vlan   +--->+    bond1    +---+
                                                  +-------------+    +-------------+



   NETWORK NODE
                                     +-------------+    +-------------+
                     +->"If VXLAN"+->+  *bond#.#00 +--->+ *br-vxlan   +-->
                     |               +-------------+    +-------------+  |
   +----------------+                                                     |     +-------------+
   |physical network|++                                                   +--->+|  qbr bridge |+--> Neutron DHCP/Router
   +----------------+                                                     |     +-------------+
                     |               +-------------+    +-------------+  |
                     +->"If  VLAN"+->+   bond1     +--->+  br-vlan    +-->
                                     +-------------+    +-------------+

**Data flow example (for OVN)**

.. code-block:: console

      COMPUTE NODE
                                                   +-------------+    +-------------+
                                  +->"If Geneve"+->+  *br-vxlan  +--->+  bond0.#00  +---+
                                  |                +-------------+    +-------------+   |
                   +-------------+                                                      |   +-----------------+
   Instance +--->  |   br-int    |++                                                    +-->| physical network|
                   +-------------+                                                      |   +-----------------+
                                  |              +-------------+    +-------------+     |
                                  +->"If VLAN"+->+   br-vlan   +--->+    bond1    +-----+
                                                 +-------------+    +-------------+


Preliminary troubleshooting questions to answer:
------------------------------------------------

- Which compute node is hosting the instance in question?
- Which interface is used for provider network traffic?
- Which interface is used for VXLAN (Geneve) overlay?
- Is there connectivity issue ingress to the instance?
- Is there connectivity issue egress from the instance?
- What is the source address of the traffic?
- What is the destination address of the traffic?
- Is there a Neutron Router in play?
- Which network node (container) is the router hosted?
- What is the project network type?

If VLAN:

Does physical interface show link and all VLANs properly trunked
across physical network?

No:
    - Check cable, seating, physical switchport configuration,
      interface/bonding configuration, and general network configuration.
      See general network troubleshooting documentation.

Yes:
    - Good!
    - Continue!

.. important::

   Do not continue until physical network is properly configured.

Does the instance's IP address ping from network's DHCP namespace
or other instances in the same network?

No:
    - Check nova console logs to see if the instance
      ever received its IP address initially.
    - Check ``security-group-rules``,
      consider adding allow ICMP rule for testing.
    - Check that OVS bridges contain the proper interfaces
      on compute and network nodes.
    - Check Neutron DHCP agent logs.
    - Check syslogs.
    - Check Neutron Open vSwitch agent logs.

Yes:
    - Good! This suggests that the instance received its IP address
      and can reach local network resources.
    - Continue!

.. important::

   Do not continue until instance has an IP address and can reach local
   network resources like DHCP.

Does the instance's IP address ping from the gateway device
(Neutron Router namespace or another gateway device)?

No:
    - Check Neutron L3 agent logs (if applicable).
    - Check Neutron Open vSwitch logs.
    - Check physical interface mappings.
    - Check Neutron router ports (if applicable).
    - Check that OVS bridges contain the proper interfaces
      on compute and network nodes.
    - Check ``security-group-rules``,
      consider adding allow ICMP rule for testing.
      In case of using OVN check additionally:
    - Check ovn-controller on all nodes.
    - Verify ovn-northd is running and DBs are healthy.
    - Ensure ovn-metadata-agent is active.
    - Review logs for ovn-controller, ovn-northd.

Yes:
    - Good! The instance can ping its intended gateway.
      The issue may be north of the gateway
      or related to the provider network.
    - Check "gateway" or host routes on the Neutron subnet.
    - Check ``security-group-rules``,
      consider adding ICMP rule for testing.
    - Check Floating IP associations (if applicable).
    - Check Neutron Router external gateway information (if applicable).
    - Check upstream routes, NATs or access-control-lists.

.. important::

   Do not continue until the instance can reach its gateway.

If VXLAN (Geneve):

Does physical interface show link and all VLANs properly trunked
across physical network?

No:
    - Check cable, seating, physical switchport configuration,
      interface/bonding configuration, and general network configuration.
      See general network troubleshooting documentation.

Yes:
    - Good!
    - Continue!

.. important::

   Do not continue until physical network is properly configured.

Are VXLAN (Geneve) VTEP addresses able to ping each other?

No:
    - Check ``br-vxlan`` interface on Compute and Network nodes.
    - Check veth pairs between containers and Linux bridges on the host.
    - Check that OVS bridges contain the proper interfaces
      on compute and network nodes.

Yes:
    - Check ml2 config file for local VXLAN (Geneve) IP
      and other VXLAN (Geneve) configuration settings.
    - Check VTEP learning method (multicast or l2population):
        - If multicast, make sure the physical switches are properly
          allowing and distributing multicast traffic.

.. important::

   Do not continue until VXLAN (Geneve) endpoints have reachability to each other.

Does the instance's IP address ping from network's DHCP namespace
or other instances in the same network?

No:
    - Check Nova console logs to see if the instance
      ever received its IP address initially.
    - Check ``security-group-rules``,
      consider adding allow ICMP rule for testing.
    - Check that OVS bridges contain the proper interfaces
      on compute and network nodes.
    - Check Neutron DHCP agent logs.
    - Check syslogs.
    - Check Neutron Open vSwitch agent logs.
    - Check that Bridge Forwarding Database (fdb) contains the proper
      entries on both the compute and Neutron agent container
      (``ovs-appctl fdb/show br-int``).

Yes:
    - Good! This suggests that the instance received its IP address
      and can reach local network resources.

.. important::

   Do not continue until instance has an IP address and can reach local network
   resources.

Does the instance's IP address ping from the gateway device
(Neutron Router namespace or another gateway device)?

No:
    - Check Neutron L3 agent logs (if applicable).
    - Check Neutron Open vSwitch agent logs.
    - Check physical interface mappings.
    - Check Neutron router ports (if applicable).
    - Check that OVS bridges contain the proper interfaces
      on compute and network nodes.
    - Check ``security-group-rules``,
      consider adding allow ICMP rule for testing.
    - Check that Bridge Forwarding Database (fdb) contains
      the proper entries on both the compute and Neutron agent container
      (``ovs-appctl fdb/show br-int``).
      In case of using OVN check additionally:
    - Check ovn-controller on all nodes.
    - Verify ovn-northd is running and DBs are healthy.
    - Ensure ovn-metadata-agent is active.
    - Review logs for ovn-controller, ovn-northd.


Yes:
    - Good! The instance can ping its intended gateway.
    - Check gateway or host routes on the Neutron subnet.
    - Check ``security-group-rules``,
      consider adding ICMP rule for testing.
    - Check Neutron Floating IP associations (if applicable).
    - Check Neutron Router external gateway information (if applicable).
    - Check upstream routes, NATs or ``access-control-lists``.

Diagnose Image service issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``glance-api`` handles the API interactions and image store.

To troubleshoot problems or errors with the Image service, refer to
:file:`/var/log/glance-api.log` inside the glance api container.

You can also conduct the following activities which may generate logs to help
identity problems:

#. Download an image to ensure that an image can be read from the store.
#. Upload an image to test whether the image is registering and writing to the
   image store.
#. Run the ``openstack image list`` command to ensure that the API and
   registry is working.

For an example and more information, see `Verify operation
<https://docs.openstack.org/glance/latest/install/verify.html>`_
and `Manage Images
<https://docs.openstack.org/glance/latest/admin/manage-images.html>`_.

Cached Ansible facts issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the beginning of a playbook run, information about each host is gathered,
such as:

* Linux distribution
* Kernel version
* Network interfaces

To improve performance, particularly in large deployments, you can
cache host facts and information.

OpenStack-Ansible enables fact caching by default. The facts are
cached in JSON files within ``/etc/openstack_deploy/ansible_facts``.

Fact caching can be disabled by running
``export ANSIBLE_CACHE_PLUGIN=memory``.
To set this permanently, set this variable in
``/usr/local/bin/openstack-ansible.rc``.
Refer to the Ansible documentation on `fact caching`_ for more details.

.. _fact caching: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_vars_facts.html

Forcing regeneration of cached facts
------------------------------------

Cached facts may be incorrect if the host receives a kernel upgrade or new
network interfaces. Newly created bridges also disrupt cache facts.

This can lead to unexpected errors while running playbooks, and require cached
facts to be regenerated.

Run the following command to remove all currently cached facts for all hosts:

.. code-block:: shell-session

   # rm /etc/openstack_deploy/ansible_facts/*

New facts will be gathered and cached during the next playbook run.

To clear facts for a single host, find its file within
``/etc/openstack_deploy/ansible_facts/`` and remove it. Each host has
a JSON file that is named after its hostname. The facts for that host
will be regenerated on the next playbook run.

Failed Ansible playbooks during an upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Container networking issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All LXC containers on the host have at least two virtual Ethernet interfaces:

* `eth0` in the container connects to `lxcbr0` on the host
* `eth1` in the container connects to `br-mgmt` on the host

.. note::

   Some containers, such as ``cinder``, ``glance``, ``neutron_agents``, and
   ``swift_proxy`` have more than two interfaces to support their
   functions.

Predictable interface naming
----------------------------

On the host, all virtual Ethernet devices are named based on their
container as well as the name of the interface inside the container:

.. code-block:: shell-session

   ${CONTAINER_UNIQUE_ID}_${NETWORK_DEVICE_NAME}

As an example, an all-in-one (AIO) build might provide a utility
container called `aio1_utility_container-d13b7132`. That container
will have two network interfaces: `d13b7132_eth0` and `d13b7132_eth1`.

Another option would be to use the LXC tools to retrieve information
about the utility container. For example:

.. code-block:: shell-session

   # lxc-info -n aio1_utility_container-d13b7132

   Name:           aio1_utility_container-d13b7132
   State:          RUNNING
   PID:            8245
   IP:             10.0.3.201
   IP:             172.29.237.204
   CPU use:        79.18 seconds
   BlkIO use:      678.26 MiB
   Memory use:     613.33 MiB
   KMem use:       0 bytes
   Link:           d13b7132_eth0
    TX bytes:      743.48 KiB
    RX bytes:      88.78 MiB
    Total bytes:   89.51 MiB
   Link:           d13b7132_eth1
    TX bytes:      412.42 KiB
    RX bytes:      17.32 MiB
    Total bytes:   17.73 MiB

The ``Link:`` lines will show the network interfaces that are attached
to the utility container.

Review container networking traffic
-----------------------------------

To dump traffic on the ``br-mgmt`` bridge, use ``tcpdump`` to see all
communications between the various containers. To narrow the focus,
run ``tcpdump`` only on the desired network interface of the
containers.

Restoring inventory from backup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible maintains a running archive of inventory. If a change has
been introduced into the system that has broken inventory or otherwise has
caused an unforseen issue, the inventory can be reverted to an early version.
The backup file ``/etc/openstack_deploy/backup_openstack_inventory.tar``
contains a set of timestamped inventories that can be restored as needed.

Example inventory restore process.

.. code-block:: bash

    mkdir /tmp/inventory_restore
    cp /etc/openstack_deploy/backup_openstack_inventory.tar /tmp/inventory_restore/backup_openstack_inventory.tar
    cd /tmp/inventory_restore
    tar xf backup_openstack_inventory.tar
    # Identify the inventory you wish to restore as the running inventory
    cp openstack_inventory.json-YYYYMMDD_SSSSSS.json /etc/openstack_deploy/openstack_inventory.json
    cd -
    rm -rf /tmp/inventory_restore

At the completion of this operation the inventory will be restored to the
earlier version.
