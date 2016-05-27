`Home <index.html>`_ OpenStack-Ansible Installation Guide

=======================
Configuring the network
=======================

This section describes the recommended network architecture.
Some components are mandatory, such as the bridges described below. We
recommend other components such as a bonded network interface but this
is not a requirement.

.. important::
   
   Follow the reference design as closely as possible for production deployments.

Although Ansible automates most deployment operations, networking on
target hosts requires manual configuration as it varies
dramatically per environment. For demonstration purposes, these
instructions use a reference architecture with example network interface
names, networks, and IP addresses. Modify these values as needed for your
particular environment.

Bonded network interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~

The reference architecture includes bonded network interfaces, which
use multiple physical network interfaces for better redundancy and throughput.
Avoid using two ports on the same multi-port network card for the same bonded
interface since a network card failure affects both physical network
interfaces used by the bond.

The ``bond0`` interface carries traffic from the containers
running your OpenStack infrastructure. Configure a static IP address on the
``bond0`` interface from your management network.

The ``bond1`` interface carries traffic from your virtual machines.
Do not configure a static IP on this interface, since neutron uses this
bond to handle VLAN and VXLAN networks for virtual machines.

Additional bridge networks are required for OpenStack-Ansible. These bridges
connect the two bonded network interfaces.

Adding bridges
~~~~~~~~~~~~~~

The combination of containers and flexible deployment options require
implementation of advanced Linux networking features, such as bridges and
namespaces.

Bridges provide layer 2 connectivity (similar to switches) among
physical, logical, and virtual network interfaces within a host. After
creating a bridge, the network interfaces are virtually plugged in to
it.

OpenStack-Ansible uses bridges to connect physical and logical network
interfaces on the host to virtual network interfaces within containers.

Namespaces provide logically separate layer 3 environments (similar to
routers) within a host. Namespaces use virtual interfaces to connect
with other namespaces, including the host namespace. These interfaces,
often called ``veth`` pairs, are virtually plugged in between
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

   -  This bridge is **required**, but LXC configures it automatically.

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

   -  Manually creates and attaches to a physical or logical interface,
      typically a ``bond0`` VLAN subinterface. Also attaches to ``eth1``
      in each container. The container network interface
      is configurable in ``openstack_user_config.yml``.

-  Storage ``br-storage``:

   -  This bridge is *optional*, but recommended.

   -  Provides segregated access to Block Storage devices between
      Compute and Block Storage hosts.

   -  Manually creates and attaches to a physical or logical interface,
      typically a ``bond0`` VLAN subinterface. Also attaches to ``eth2``
      in each associated container. The container network
      interface is configurable in ``openstack_user_config.yml``.

-  OpenStack Networking tunnel ``br-vxlan``:

   -  This bridge is **required**.

   -  Provides infrastructure for VXLAN tunnel networks.

   -  Manually creates and attaches to a physical or logical interface,
      typically a ``bond1`` VLAN subinterface. Also attaches to
      ``eth10`` in each associated container. The
      container network interface is configurable in
      ``openstack_user_config.yml``.

-  OpenStack Networking provider ``br-vlan``:

   -  This bridge is **required**.

   -  Provides infrastructure for VLAN networks.

   -  Manually creates and attaches to a physical or logical interface,
      typically ``bond1``. Attaches to ``eth11`` for vlan type networks
      in each associated container. It does not contain an IP address because
      it only handles layer 2 connectivity. The
      container network interface is configurable in
      ``openstack_user_config.yml``.

   -  This interface supports flat networks with additional
      bridge configuration. More details are available here:
      :ref:`network_configuration`.


Network diagrams
~~~~~~~~~~~~~~~~

The following image shows how all of the interfaces and bridges interconnect
to provide network connectivity to the OpenStack deployment:

.. image:: figures/networkarch-container-external.png

OpenStack-Ansible deploys the compute service on the physical host rather than
in a container. The following image shows how to use bridges for
network connectivity:

.. image:: figures/networkarch-bare-external.png

The following image shows how the neutron agents work with the bridges
``br-vlan`` and ``br-vxlan``. OpenStack Networking (neutron) is
configured to use a DHCP agent, L3 agent, and Linux Bridge agent within a
``networking-agents`` container. The image shows how DHCP agents provide
information (IP addresses and DNS servers) to the instances, and how
routing works on the image:

.. image:: figures/networking-neutronagents.png

The following image shows how virtual machines connect to the ``br-vlan`` and
``br-vxlan`` bridges and send traffic to the network outside the host:

.. image:: figures/networking-compute.png


--------------

.. include:: navigation.txt
