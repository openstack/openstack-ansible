`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the network
-----------------------

This documentation section describes a recommended reference architecture.
Some components are mandatory, such as the bridges described below. Other
components aren't required but are strongly recommended, such as the bonded
network interfaces. Deployers are strongly urged to follow the reference
design as closely as possible for production deployments.

Although Ansible automates most deployment operations, networking on
target hosts requires manual configuration because it can vary
dramatically per environment. For demonstration purposes, these
instructions use a reference architecture with example network interface
names, networks, and IP addresses. Modify these values as needed for the
particular environment.

Bonded network interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~

The reference architecture includes bonded network interfaces, which
use multiple physical network interfaces for better redundancy and throughput.
Avoid using two ports on the same multi-port network card for the same bonded
interface since a network card failure would affect both physical network
interfaces used by the bond.

The ``bond0`` interface will carry the traffic from the containers that
run the OpenStack infrastructure. Configure a static IP address on the
``bond0`` interface from your management network.

The ``bond1`` interface will carry the traffic from your virtual machines.
Don't configure a static IP on this interface since this bond will be used by
neutron to handle VLAN and VXLAN networks for virtual machines.

Additional bridge networks are required for OpenStack-Ansible and those bridges
will be connected to these two bonded network interfaces. See the following
section for the bridge configuration.

Adding bridges
~~~~~~~~~~~~~~

The combination of containers and flexible deployment options requires
implementation of advanced Linux networking features such as bridges and
namespaces.

*Bridges* provide layer 2 connectivity (similar to switches) among
physical, logical, and virtual network interfaces within a host. After
creating a bridge, the network interfaces are virtually "plugged in" to
it.

OpenStack-Ansible uses bridges to connect physical and logical network
interfaces on the host to virtual network interfaces within containers.

*Namespaces* provide logically separate layer 3 environments (similar to
routers) within a host. Namespaces use virtual interfaces to connect
with other namespaces, including the host namespace. These interfaces,
often called ``veth`` pairs, are virtually "plugged in" between
namespaces similar to patch cables connecting physical devices such as
switches and routers.

Each container has a namespace that connects to the host namespace with
one or more ``veth`` pairs. Unless specified, the system generates
random names for ``veth`` pairs.

The following image demonstrates how the container network interfaces are
connected to the host's bridges and to the host's physical network interfaces:

.. image:: figures/networkcomponents.png

Target hosts can contain the following network bridges:

-  LXC internal ``lxcbr0``:

   -  This bridge is **required**, but LXC will configure it automatically.

   -  Provides external (typically internet) connectivity to containers.

   -  This bridge does not directly attach to any physical or logical
      interfaces on the host because iptables handles connectivity. It
      attaches to ``eth0`` in each container, but the container network
      interface is configurable in ``openstack_user_config.yml`` in the
      ``provider_networks`` dictionary.

-  Container management ``br-mgmt``:

   -  This bridge is **required**.

   -  Provides management of and communication among infrastructure and
      OpenStack services.

   -  Manually created and attaches to a physical or logical interface,
      typically a ``bond0`` VLAN subinterface. Also attaches to ``eth1``
      in each container. As mentioned earlier, the container network interface
      is configurable in ``openstack_user_config.yml``.

-  Storage ``br-storage``:

   -  This bridge is *optional*, but recommended.

   -  Provides segregated access to block storage devices between
      Compute and Block Storage hosts.

   -  Manually created and attaches to a physical or logical interface,
      typically a ``bond0`` VLAN subinterface. Also attaches to ``eth2``
      in each associated container. As mentioned earlier, the container network
      interface is configurable in ``openstack_user_config.yml``.

-  OpenStack Networking tunnel/overlay ``br-vxlan``:

   -  This bridge is **required**.

   -  Provides infrastructure for VXLAN tunnel/overlay networks.

   -  Manually created and attaches to a physical or logical interface,
      typically a ``bond1`` VLAN subinterface. Also attaches to
      ``eth10`` in each associated container. As mentioned earlier, the
      container network interface is configurable in
      ``openstack_user_config.yml``.

-  OpenStack Networking provider ``br-vlan``:

   -  This bridge is **required**.

   -  Provides infrastructure for VLAN networks.

   -  Manually created and attaches to a physical or logical interface,
      typically ``bond1``. Attaches to ``eth11`` for vlan type networks
      in each associated container. It does not contain an IP address because
      it only handles layer 2 connectivity.  As mentioned earlier, the
      container network interface is configurable in
      ``openstack_user_config.yml``.

   -  This interface can support flat networks as well, though additional
      bridge configuration will be needed. More details are available here:
      :ref:`network_configuration`.


Network diagrams
~~~~~~~~~~~~~~~~

The following image shows how all of the interfaces and bridges interconnect
to provide network connectivity to the OpenStack deployment:

.. image:: figures/networkarch-container-external.png

OpenStack-Ansible deploys the compute service on the physical host rather than
in a container. The following image shows how the bridges are used for
network connectivity:

.. image:: figures/networkarch-bare-external.png

The following image shows how the neutron agents work with the bridges
``br-vlan`` and ``br-vxlan``. As a reminder, OpenStack Networking (neutron) is
configured to use a DHCP agent, L3 agent and Linux Bridge agent within a
``networking-agents`` container. You can see how the DHCP agents can provide
information (IP addresses and DNS servers) to the instances, but also how
routing works on the image:

.. image:: figures/networking-neutronagents.png

The following image shows how virtual machines connect to the ``br-vlan`` and
``br-vxlan`` bridges and send traffic to the network outside the host:

.. image:: figures/networking-compute.png


--------------

.. include:: navigation.txt
