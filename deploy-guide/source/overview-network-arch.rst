.. _network-architecture:

====================
Network architecture
====================

Although Ansible automates most deployment operations, networking on target
hosts requires manual configuration because it varies from one use case to
another. This section describes the network configuration that must be
implemented on all target hosts.

For more information about how networking works, see :ref:`network-appendix`.

Host network bridges
~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible uses bridges to connect physical and logical network
interfaces on the host to virtual network interfaces within containers.
Target hosts are configured with the following network bridges.


*  LXC internal: ``lxcbr0``

   The ``lxcbr0`` bridge is **required**, but OpenStack-Ansible configures it
   automatically. It provides external (typically Internet) connectivity to
   containers.

   This bridge does not directly attach to any physical or logical
   interfaces on the host because iptables handles connectivity. It
   attaches to ``eth0`` in each container.

   The container network that the bridge attaches to is configurable in the
   ``openstack_user_config.yml`` file in the ``provider_networks``
   dictionary.

*  Container management: ``br-mgmt``

   The ``br-mgmt`` bridge is **required**. It provides management of and
   communication between the infrastructure and OpenStack services.

   The bridge attaches to a physical or logical interface, typically a
   ``bond0`` VLAN subinterface. It also attaches to ``eth1`` in each container.

   The container network interface that the bridge attaches to is configurable
   in the ``openstack_user_config.yml`` file.

*  Storage:``br-storage``

   The ``br-storage`` bridge is **optional**, but recommended for production
   environments. It provides segregated access to Block Storage devices
   between OpenStack services and Block Storage devices.

   The bridge attaches to a physical or logical interface, typically a
   ``bond0`` VLAN subinterface. It also attaches to ``eth2`` in each
   associated container.

   The container network interface that the bridge attaches to is configurable
   in the ``openstack_user_config.yml`` file.

*  OpenStack Networking tunnel: ``br-vxlan``

   The ``br-vxlan`` bridge is **required** if the environment is configured to
   allow projects to create virtual networks. It provides the interface for
   virtual (VXLAN) tunnel networks.

   The bridge attaches to a physical or logical interface, typically a
   ``bond1`` VLAN subinterface. It also attaches to ``eth10`` in each
   associated container.

   The container network interface it attaches to is configurable in
   the ``openstack_user_config.yml`` file.

*  OpenStack Networking provider: ``br-vlan``

   The ``br-vlan`` bridge is **required**. It provides infrastructure for VLAN
   tagged or flat (no VLAN tag) networks.

   The bridge attaches to a physical or logical interface, typically ``bond1``.
   It attaches to ``eth11`` for VLAN type networks in each associated
   container. It is not assigned an IP address because it handles only
   layer 2 connectivity.

   The container network interface that the bridge attaches to is configurable
   in the ``openstack_user_config.yml`` file.

