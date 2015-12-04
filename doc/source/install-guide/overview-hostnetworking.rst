`Home <index.html>`_ OpenStack-Ansible Installation Guide

Host networking
---------------

The combination of containers and flexible deployment options requires
implementation of advanced Linux networking features such as bridges and
namespaces.

*Bridges* provide layer 2 connectivity (similar to switches) among
physical, logical, and virtual network interfaces within a host. After
creating a bridge, the network interfaces are virtually "plugged in" to
it.

OSA uses bridges to connect physical and logical network interfaces
on the host to virtual network interfaces within containers.

*Namespaces* provide logically separate layer 3 environments (similar to
routers) within a host. Namespaces use virtual interfaces to connect
with other namespaces including the host namespace. These interfaces,
often called ``veth`` pairs, are virtually "plugged in" between
namespaces similar to patch cables connecting physical devices such as
switches and routers.

Each container has a namespace that connects to the host namespace with
one or more ``veth`` pairs. Unless specified, the system generates
random names for ``veth`` pairs.

The relationship between physical interfaces, logical interfaces,
bridges, and virtual interfaces within containers is shown in
`Figure 2.2, "Network
components" <overview-hostnetworking.html#fig_overview_networkcomponents>`_.

 

**Figure 2.2. Network components**

.. image:: figures/networkcomponents.png

Target hosts can contain the following network bridges:

-  LXC internal ``lxcbr0``:

   -  Mandatory (automatic).

   -  Provides external (typically internet) connectivity to containers.

   -  Automatically created and managed by LXC. Does not directly attach
      to any physical or logical interfaces on the host because iptables
      handle connectivity. Attaches to ``eth0`` in each container.

-  Container management ``br-mgmt``:

   -  Mandatory.

   -  Provides management of and communication among infrastructure and
      OpenStack services.

   -  Manually created and attaches to a physical or logical interface,
      typically a ``bond0`` VLAN subinterface. Also attaches to ``eth1``
      in each container.

-  Storage ``br-storage``:

   -  Optional.

   -  Provides segregated access to block storage devices between
      Compute and Block Storage hosts.

   -  Manually created and attaches to a physical or logical interface,
      typically a ``bond0`` VLAN subinterface. Also attaches to ``eth2``
      in each associated container.

-  OpenStack Networking tunnel/overlay ``br-vxlan``:

   -  Mandatory.

   -  Provides infrastructure for VXLAN tunnel/overlay networks.

   -  Manually created and attaches to a physical or logical interface,
      typically a ``bond1`` VLAN subinterface. Also attaches to
      ``eth10`` in each associated container.

-  OpenStack Networking provider ``br-vlan``:

   -  Mandatory.

   -  Provides infrastructure for VLAN networks.

   -  Manually created and attaches to a physical or logical interface,
      typically ``bond1``. Attaches to ``eth11`` for vlan type networks
      in each associated container. It does not contain an IP address because
      it only handles layer 2 connectivity. This interface can support flat
      networks as well, though additional bridge configuration will be needed.
      See more on `network configuration here <configure-networking.html>`_


`Figure 2.3, "Container network
architecture" <overview-hostnetworking.html#fig_overview_networkarch-container>`_
provides a visual representation of network components for services in
containers.


**Figure 2.3. Container network architecture**

.. image:: figures/networkarch-container-external.png

By default, OSA installs the Compute service in a bare metal
environment rather than within a container. `Figure 2.4, "Bare/Metal
network
architecture" <overview-hostnetworking.html#fig_overview_networkarch-bare>`_
provides a visual representation of the unique layout of network
components on a Compute host.

 

**Figure 2.4. Bare/Metal network architecture**

.. image:: figures/networkarch-bare-external.png

--------------

.. include:: navigation.txt
