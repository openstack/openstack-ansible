Configuring the network
=======================

OpenStack-Ansible uses bridges to connect physical and logical network
interfaces on the host to virtual network interfaces within containers.
Target hosts need to be configured with the following network bridges:

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

For a detailed reference of how the host and container networking is
implemented, refer to
:dev_docs:`OpenStack-Ansible Reference Architecture, section Container Networking <reference/architecture/index.html>`.

For use case examples, refer to
:dev_docs:`User Guides <user/index.html>`.


Host network bridges information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*  LXC internal: ``lxcbr0``

   The ``lxcbr0`` bridge is **required** for LXC, but OpenStack-Ansible
   configures it automatically. It provides external (typically Internet)
   connectivity to containers with dnsmasq (DHCP/DNS) + NAT.

   This bridge does not directly attach to any physical or logical
   interfaces on the host because iptables handles connectivity. It
   attaches to ``eth0`` in each container.

   The container network that the bridge attaches to is configurable in the
   ``openstack_user_config.yml`` file in the ``provider_networks``
   dictionary.

*  Container management: ``br-mgmt``

   The ``br-mgmt`` bridge provides management of and
   communication between the infrastructure and OpenStack services.

   The bridge attaches to a physical or logical interface, typically a
   ``bond0`` VLAN subinterface. It also attaches to ``eth1`` in each container.

   The container network interface that the bridge attaches to is configurable
   in the ``openstack_user_config.yml`` file.

*  Storage: ``br-storage``

   The ``br-storage`` bridge provides segregated access to Block Storage
   devices between OpenStack services and Block Storage devices.

   The bridge attaches to a physical or logical interface, typically a
   ``bond0`` VLAN subinterface. It also attaches to ``eth2`` in each
   associated container.

   The container network interface that the bridge attaches to is configurable
   in the ``openstack_user_config.yml`` file.

*  OpenStack Networking tunnel: ``br-vxlan``

   The ``br-vxlan`` interface is **required if** the environment is configured to
   allow projects to create virtual networks using VXLAN.
   It provides the interface for encapsulated virtual (VXLAN) tunnel network traffic.

   Note that ``br-vxlan`` is not required to be a bridge at all, a physical interface
   or a bond VLAN subinterface can be used directly and will be more efficient. The name
   ``br-vxlan`` is maintained here for consistency in the documentation and example
   configurations.

   The container network interface it attaches to is configurable in
   the ``openstack_user_config.yml`` file.

*  OpenStack Networking provider: ``br-vlan``

   The ``br-vlan`` bridge is provides infrastructure for VLAN
   tagged or flat (no VLAN tag) networks.

   The bridge attaches to a physical or logical interface, typically ``bond1``.
   It is not assigned an IP address because it handles only
   layer 2 connectivity.

   The container network interface that the bridge attaches to is configurable
   in the ``openstack_user_config.yml`` file.
