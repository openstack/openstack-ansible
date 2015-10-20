`Home <index.html>`_ OpenStack-Ansible Installation Guide

Reference architecture
----------------------

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

--------------

.. include:: navigation.txt
