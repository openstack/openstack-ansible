`Home <index.html>`_ OpenStack-Ansible Installation Guide

======================
Reference architecture
======================

Overview
~~~~~~~~

This example allows you to use your own parameters for the deployment.

The following is a table of the bridges that are be configured on hosts, if you followed the
previously proposed design.

+-------------+-----------------------+-------------------------------------+
| Bridge name | Best configured on    | With a static IP                    |
+=============+=======================+=====================================+
| br-mgmt     | On every node         | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every storage node | When component is deployed on metal |
+ br-storage  +-----------------------+-------------------------------------+
|             | On every compute node | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every network node | When component is deployed on metal |
+ br-vxlan    +-----------------------+-------------------------------------+
|             | On every compute node | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every network node | Never                               |
+ br-vlan     +-----------------------+-------------------------------------+
|             | On every compute node | Never                               |
+-------------+-----------------------+-------------------------------------+

Modifying the network interfaces file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After establishing initial host management network connectivity using
the ``bond0`` interface, modify the ``/etc/network/interfaces`` file as
described in the following procedure.

**Procedure 4.1. Modifying the network interfaces file**

#. Physical interfaces:

   .. code-block:: yaml

       # Physical interface 1
       auto eth0
       iface eth0 inet manual
           bond-master bond0
           bond-primary eth0

       # Physical interface 2
       auto eth1
       iface eth1 inet manual
           bond-master bond1
           bond-primary eth1

       # Physical interface 3
       auto eth2
       iface eth2 inet manual
           bond-master bond0

       # Physical interface 4
       auto eth3
       iface eth3 inet manual
           bond-master bond1

#. Bonding interfaces:

   .. code-block:: yaml

       # Bond interface 0 (physical interfaces 1 and 3)
       auto bond0
       iface bond0 inet static
           bond-slaves eth0 eth2
           bond-mode active-backup
           bond-miimon 100
           bond-downdelay 200
           bond-updelay 200
           address HOST_IP_ADDRESS
           netmask HOST_NETMASK
           gateway HOST_GATEWAY
           dns-nameservers HOST_DNS_SERVERS

       # Bond interface 1 (physical interfaces 2 and 4)
       auto bond1
       iface bond1 inet manual
           bond-slaves eth1 eth3
           bond-mode active-backup
           bond-miimon 100
           bond-downdelay 250
           bond-updelay 250

   If not already complete, replace ``HOST_IP_ADDRESS``,
   ``HOST_NETMASK``, ``HOST_GATEWAY``, and ``HOST_DNS_SERVERS``
   with the appropriate configuration for the host management network.

#. Logical (VLAN) interfaces:

   .. code-block:: yaml

       # Container management VLAN interface
       iface bond0.CONTAINER_MGMT_VLAN_ID inet manual
           vlan-raw-device bond0

       # OpenStack Networking VXLAN (tunnel/overlay) VLAN interface
       iface bond1.TUNNEL_VLAN_ID inet manual
           vlan-raw-device bond1

       # Storage network VLAN interface (optional)
       iface bond0.STORAGE_VLAN_ID inet manual
           vlan-raw-device bond0

   Replace ``*_VLAN_ID`` with the appropriate configuration for the
   environment.

#. Bridge devices:

   .. code-block:: yaml

       # Container management bridge
       auto br-mgmt
       iface br-mgmt inet static
           bridge_stp off
           bridge_waitport 0
           bridge_fd 0
           # Bridge port references tagged interface
           bridge_ports bond0.CONTAINER_MGMT_VLAN_ID
           address CONTAINER_MGMT_BRIDGE_IP_ADDRESS
           netmask CONTAINER_MGMT_BRIDGE_NETMASK
           dns-nameservers CONTAINER_MGMT_BRIDGE_DNS_SERVERS

       # OpenStack Networking VXLAN (tunnel/overlay) bridge
       auto br-vxlan
       iface br-vxlan inet static
           bridge_stp off
           bridge_waitport 0
           bridge_fd 0
           # Bridge port references tagged interface
           bridge_ports bond1.TUNNEL_VLAN_ID
           address TUNNEL_BRIDGE_IP_ADDRESS
           netmask TUNNEL_BRIDGE_NETMASK

       # OpenStack Networking VLAN bridge
       auto br-vlan
       iface br-vlan inet manual
           bridge_stp off
           bridge_waitport 0
           bridge_fd 0
           # Bridge port references untagged interface
           bridge_ports bond1

       # Storage bridge (optional)
       auto br-storage
       iface br-storage inet static
           bridge_stp off
           bridge_waitport 0
           bridge_fd 0
           # Bridge port reference tagged interface
           bridge_ports bond0.STORAGE_VLAN_ID
           address STORAGE_BRIDGE_IP_ADDRESS
           netmask STORAGE_BRIDGE_NETMASK

   Replace ``*_VLAN_ID``, ``*_BRIDGE_IP_ADDRESS``, and
   ``*_BRIDGE_NETMASK``, ``*_BRIDGE_DNS_SERVERS`` with the
   appropriate configuration for the environment.

Example for 3 controller nodes and 2 compute nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- VLANs:

  -  Host management: Untagged/Native
  -  Container management: 10
  -  Tunnels: 30
  -  Storage: 20

- Networks:

  -  Host management: 10.240.0.0/22
  -  Container management: 172.29.236.0/22
  -  Tunnel: 172.29.240.0/22
  -  Storage: 172.29.244.0/22

- Addresses for the controller nodes:

  -  Host management: 10.240.0.11 - 10.240.0.13
  -  Host management gateway: 10.240.0.1
  -  DNS servers: 69.20.0.164 69.20.0.196
  -  Container management: 172.29.236.11 - 172.29.236.13
  -  Tunnel: no IP (because IP exist in the containers, when the components aren't deployed directly on metal)
  -  Storage: no IP (because IP exist in the containers, when the components aren't deployed directly on metal)

- Addresses for the compute nodes:

  -  Host management: 10.240.0.21 - 10.240.0.22
  -  Host management gateway: 10.240.0.1
  -  DNS servers: 69.20.0.164 69.20.0.196
  -  Container management: 172.29.236.21 - 172.29.236.22
  -  Tunnel: 172.29.240.21 - 172.29.240.22
  -  Storage: 172.29.244.21 - 172.29.244.22

--------------

.. include:: navigation.txt
