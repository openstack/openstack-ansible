.. _network-architecture:

====================
Network architecture
====================

Although Ansible automates most deployment operations, networking on
target hosts requires manual configuration as it varies from one use-case
to another.

The following section describes the network configuration that must be
implemented on all target hosts.

A deeper explanation of how the networking works can be found in
:ref:`network-appendix`.

Host network bridges
~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible uses bridges to connect physical and logical network
interfaces on the host to virtual network interfaces within containers.

Target hosts are configured with the following network bridges:

*  LXC internal ``lxcbr0``:

   * This bridge is **required**, but OpenStack-Ansible configures it
     automatically.

   * Provides external (typically internet) connectivity to containers.

   * This bridge does not directly attach to any physical or logical
     interfaces on the host because iptables handles connectivity. It
     attaches to ``eth0`` in each container, but the container network
     interface it attaches to is configurable in
     ``openstack_user_config.yml`` in the ``provider_networks``
     dictionary.

*  Container management ``br-mgmt``:

   * This bridge is **required**.

   * Provides management of and communication between the infrastructure
     and OpenStack services.

   * Attaches to a physical or logical interface, typically a ``bond0`` VLAN
     subinterface. Also attaches to ``eth1`` in each container. The container
     network interface it attaches to is configurable in
     ``openstack_user_config.yml``.

*  Storage ``br-storage``:

   *  This bridge is **optional**, but recommended for production
      environments.

   *  Provides segregated access to Block Storage devices between
      OpenStack services and Block Storage devices.

   *  Attaches to a physical or logical interface, typically a ``bond0`` VLAN
      subinterface. Also attaches to ``eth2`` in each associated container.
      The container network interface it attaches to is configurable in
      ``openstack_user_config.yml``.

*  OpenStack Networking tunnel ``br-vxlan``:

   -  This bridge is **required** if the environment is configured to allow
      projects to create virtual networks.

   -  Provides the interface for virtual (VXLAN) tunnel networks.

   -  Attaches to a physical or logical interface, typically a ``bond1`` VLAN
      subinterface. Also attaches to ``eth10`` in each associated container.
      The container network interface it attaches to is configurable in
      ``openstack_user_config.yml``.

-  OpenStack Networking provider ``br-vlan``:

   -  This bridge is **required**.

   -  Provides infrastructure for VLAN tagged or flat (no VLAN tag) networks.

   -  Attaches to a physical or logical interface, typically ``bond1``.
      Attaches to ``eth11`` for vlan type networks in each associated
      container. It is not assigned an IP address because it only handles
      layer 2 connectivity. The container network interface it attaches to is
      configurable in ``openstack_user_config.yml``.

