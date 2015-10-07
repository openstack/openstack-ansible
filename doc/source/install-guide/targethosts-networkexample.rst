`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the network on a target host
----------------------------------------

This example uses the following parameters to configure networking on a
single target host. See `Figure 4.2, "Target hosts for infrastructure,
networking, and storage
services" <targethosts-networkexample.html#fig_hosts-target-network-containerexample>`_
and `Figure 4.3, "Target hosts for Compute
service" <targethosts-networkexample.html#fig_hosts-target-network-bareexample>`_
for a visual representation of these parameters in the architecture.

-  VLANs:

   -  Host management: Untagged/Native

   -  Container management: 10

   -  Tunnels: 30

   -  Storage: 20

   Networks:

   -  Host management: 10.240.0.0/22

   -  Container management: 172.29.236.0/22

   -  Tunnel: 172.29.240.0/22

   -  Storage: 172.29.244.0/22

   Addresses:

   -  Host management: 10.240.0.11

   -  Host management gateway: 10.240.0.1

   -  DNS servers: 69.20.0.164 69.20.0.196

   -  Container management: 172.29.236.11

   -  Tunnel: 172.29.240.11

   -  Storage: 172.29.244.11

 

**Figure 4.2. Target hosts for infrastructure, networking, and storage
services**

.. image:: figures/networkarch-container-external-example.png

**Figure 4.3. Target hosts for Compute service**

.. image:: figures/networkarch-bare-external-example.png

Contents of the ``/etc/network/interfaces`` file:

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

.. code-block:: yaml

    # Bond interface 0 (physical interfaces 1 and 3)
    auto bond0
    iface bond0 inet static
        bond-slaves eth0 eth2
        bond-mode active-backup
        bond-miimon 100
        bond-downdelay 200
        bond-updelay 200
        address 10.240.0.11
        netmask 255.255.252.0
        gateway 10.240.0.1
        dns-nameservers 69.20.0.164 69.20.0.196

    # Bond interface 1 (physical interfaces 2 and 4)
    auto bond1
    iface bond1 inet manual
        bond-slaves eth1 eth3
        bond-mode active-backup
        bond-miimon 100
        bond-downdelay 250
        bond-updelay 250

    # Container management VLAN interface
    iface bond0.10 inet manual
        vlan-raw-device bond0

    # OpenStack Networking VXLAN (tunnel/overlay) VLAN interface
    iface bond1.30 inet manual
        vlan-raw-device bond1

    # Storage network VLAN interface (optional)
    iface bond0.20 inet manual
        vlan-raw-device bond0

    # Container management bridge
    auto br-mgmt
    iface br-mgmt inet static
        bridge_stp off
        bridge_waitport 0
        bridge_fd 0
        # Bridge port references tagged interface
        bridge_ports bond0.10
        address 172.29.236.11
        netmask 255.255.252.0
        dns-nameservers 69.20.0.164 69.20.0.196

    # OpenStack Networking VXLAN (tunnel/overlay) bridge
    auto br-vxlan
    iface br-vxlan inet static
        bridge_stp off
        bridge_waitport 0
        bridge_fd 0
        # Bridge port references tagged interface
        bridge_ports bond1.30
        address 172.29.240.11
        netmask 255.255.252.0

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
        bridge_ports bond0.20
        address 172.29.244.11
        netmask 255.255.252.0

--------------

.. include:: navigation.txt
